import clsx from "clsx";
import { useCallback, useEffect, useMemo, useState, type CSSProperties, type MouseEvent } from "react";
import ReactFlow, {
  useStore as useReactFlowStore,
  Background,
  Handle,
  Position,
  ReactFlowProvider,
  type Edge,
  type Node,
  type NodeProps,
  type ReactFlowInstance,
} from "reactflow";
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp } from "lucide-react";

import { X_UNIT, Y_UNIT, type Line, type MetroMap, type Station } from "../lib/map";
import { useAppStore } from "../store/useAppStore";
import { useMapStore } from "../store/useMapStore";
import "./MetroMapCanvas.css";

type StationNodeData = Station & {
  lineColors: Record<string, string>;
};

type EndpointDirection = "left" | "right" | "up" | "down";

type LineEndpoints = {
  startStationId: string;
  endStationId: string;
  startDirection: EndpointDirection;
  endDirection: EndpointDirection;
};

const DIRECTION_ICONS: Record<EndpointDirection, typeof ArrowLeft> = {
  left: ArrowLeft,
  right: ArrowRight,
  up: ArrowUp,
  down: ArrowDown,
};

function invertDirection(direction: EndpointDirection): EndpointDirection {
  switch (direction) {
    case "left":
      return "right";
    case "right":
      return "left";
    case "up":
      return "down";
    case "down":
      return "up";
  }
}

function directionFromDelta(dx: number, dy: number): EndpointDirection {
  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0 ? "right" : "left";
  }
  return dy >= 0 ? "down" : "up";
}

function resolveLineEndpoints(line: Line, map: MetroMap): LineEndpoints | null {
  if (!line.stations.length) return null;
  const lookup = new Map(map.stations.map((station) => [station.id, station]));
  const start = lookup.get(line.stations[0]);
  const end = lookup.get(line.stations[line.stations.length - 1]);
  if (!start || !end) return null;
  const next = lookup.get(line.stations[1]);
  const prev = lookup.get(line.stations[line.stations.length - 2]);
  const startDirection = invertDirection(
    directionFromDelta(
      next ? next.x - start.x : 1,
      next ? next.y - start.y : 0
    )
  );
  const endDirection = directionFromDelta(
    prev ? end.x - prev.x : 1,
    prev ? end.y - prev.y : 0
  );
  return {
    startStationId: start.id,
    endStationId: end.id,
    startDirection,
    endDirection,
  };
}

function arrowPositionStyle(direction: EndpointDirection): CSSProperties {
  const offset = 60;
  switch (direction) {
    case "left":
      return {
        left: "50%",
        top: "50%",
        transform: `translate(-50%, -50%) translateX(-${offset}px)`,
      };
    case "right":
      return {
        left: "50%",
        top: "50%",
        transform: `translate(-50%, -50%) translateX(${offset}px)`,
      };
    case "up":
      return {
        left: "50%",
        top: "50%",
        transform: `translate(-50%, -50%) translateY(-${offset}px)`,
      };
    case "down":
      return {
        left: "50%",
        top: "50%",
        transform: `translate(-50%, -50%) translateY(${offset}px)`,
      };
  }
}

type LocationSelectArrowProps = {
  direction: EndpointDirection;
  color: string;
  label: string;
  onSelect: () => void;
};

function LocationSelectArrow({ direction, color, label, onSelect }: LocationSelectArrowProps) {
  const Icon = DIRECTION_ICONS[direction];
  return (
    <button
      type="button"
      onClick={(event) => {
        event.stopPropagation();
        onSelect();
      }}
      className="LocationSelectArrow"
      style={{
        ...arrowPositionStyle(direction),
        "--arrow-base": color,
        "--arrow-outline": "#ffffff",
        "--arrow-outline-dark": "#0f172a",
        "--arrow-active-bg": `color-mix(in srgb, ${color} 80%, white)`,
        "--arrow-active-bg-dark": `color-mix(in srgb, ${color} 15%, white)`,
        "--shadow-color": `${color}33`,
        "--shadow-strong-color": `${color}55`,
      } as CSSProperties}
      aria-label={label}
      title={label}
    >
      <Icon className="h-4 w-4" />
    </button>
  );
}

const NODE_TYPES = {
  station: StationNode,
};

function StationNode({ data, selected }: NodeProps<StationNodeData>) {
  const { name, lines, lineColors } = data;
  const locationSelectLineId = useMapStore((state) => state.locationSelectLineId);
  const setLocationSelectLineId = useMapStore((state) => state.setLocationSelectLineId);
  const map = useMapStore((state) => state.map);
  const chatkit = useAppStore((state) => state.chatkit);

  const targetLine = useMemo(
    () => map?.lines.find((line) => line.id === locationSelectLineId),
    [locationSelectLineId, map]
  );

  const endpoints = useMemo(() => {
    if (!map || !targetLine) return null;
    return resolveLineEndpoints(targetLine, map);
  }, [map, targetLine]);

  const activePositions = useMemo(
    () => {
      if (!endpoints || !targetLine) return [];
      const positions: Array<{
        position: "start" | "end";
        direction: EndpointDirection;
        line: Line;
      }> = [];
      if (endpoints.startStationId === data.id) {
        positions.push({
          position: "start",
          direction: endpoints.startDirection,
          line: targetLine,
        });
      }
      if (endpoints.endStationId === data.id) {
        positions.push({
          position: "end",
          direction: endpoints.endDirection,
          line: targetLine,
        });
      }
      return positions;
    },
    [data.id, endpoints, targetLine]
  );

  const dotColors = lines
    .map((lineId) => lineColors[lineId])
    .filter((color): color is string => Boolean(color));
  const primaryColor = dotColors[0] ?? "#0ea5e9";
  const isExchange = dotColors.length > 1;

  const handleLocationSelection = useCallback(
    (position: "start" | "end", line: Line) => {
      setLocationSelectLineId(null);
      if (!chatkit) {
        console.warn("ChatKit unavailable, cannot report location selection.");
        return;
      }
      const positionLabel = position === "start" ? "beginning" : "end";
      const message = `I would like to add the station to the ${positionLabel} of the ${line.name} line.`;
      chatkit
        .sendUserMessage({ text: message })
        .catch((error) => console.error("Failed to send location selection.", error));
    },
    [chatkit]
  );

  return (
    <div
      className={clsx("StationNode", {"StationNode--selected": selected, "location-select-mode": !!locationSelectLineId })}
      style={{ "--station-highlight": primaryColor } as CSSProperties}
    >
      {/* Hidden handles on all sides so edges can connect based on orientation. */}
      <Handle id="target-left" type="target" position={Position.Left} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="target-right" type="target" position={Position.Right} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="target-top" type="target" position={Position.Top} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="target-bottom" type="target" position={Position.Bottom} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-left" type="source" position={Position.Left} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-right" type="source" position={Position.Right} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-top" type="source" position={Position.Top} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-bottom" type="source" position={Position.Bottom} className="!h-0 !w-0 !bg-transparent !border-0" />

      {activePositions.map(({ position, direction, line }) => (
        <LocationSelectArrow
          key={`${line.id}-${position}`}
          direction={direction}
          color={line.color}
          label={`Choose the ${position} of ${line.name}`}
          onSelect={() => handleLocationSelection(position, line)}
        />
      ))}

      <div
        className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-lg ring-2 dark:bg-slate-900"
        style={{ borderColor: primaryColor, boxShadow: `0 4px 9px -2px ${primaryColor}55` }}
      >
        {isExchange ? (
          <div className="relative flex items-center justify-center">
            {dotColors.map((color, index) => {
              const offset = (index - (dotColors.length - 1) / 2) * 8;
              return (
                <div
                  key={`${name}-${color}-${index}`}
                  className="absolute h-4 w-4 rounded-full ring-1 ring-white dark:ring-slate-900"
                  style={{
                    backgroundColor: color,
                    transform: `translateX(${offset}px)`,
                  }}
                />
              );
            })}
          </div>
        ) : (
          <div className="h-4 w-4 rounded-full" style={{ backgroundColor: primaryColor }} />
        )}
      </div>

      <span
        className="pointer-events-none absolute bottom-0 left-1/2 origin-bottom text-xs text-center whitespace-nowrap font-semibold tracking-tight text-slate-700 drop-shadow-sm dark:text-slate-200"
        style={{ transform: "rotate(-30deg) translateX(40px) translateY(-30px)" }}
        title={name}
      >
        {name}
      </span>
    </div>
  );
}

function buildGraph(map: MetroMap, selectedStationId: string | null = null): { nodes: Node[]; edges: Edge[] } {
  const nodes = buildNodes(map, selectedStationId);
  const edges = buildEdges(map, nodes);
  return { nodes, edges };
}

function buildNodes(map: MetroMap, selectedStationId: string | null): Node<StationNodeData>[] {
  const lineColor: Record<string, string> = {};
  map.lines.forEach((line) => {
    lineColor[line.id] = line.color;
  });

  return map.stations.map((station) => {
    return {
      id: station.id,
      type: "station",
      position: { x: station.x * X_UNIT, y: station.y * Y_UNIT },
      data: {
        ...station,
        lineColors: lineColor,
      },
      draggable: false,
      selectable: true,
      selected: selectedStationId === station.id,
    };
  });
}

function buildEdges(map: MetroMap, nodes: Node[]): Edge[] {
  const nodeLookup: Record<string, Node> = nodes.reduce((acc, node) => {
    acc[node.id] = node;
    return acc;
  }, {} as Record<string, Node>);

  const edges: Edge[] = [];

  map.lines.forEach((line) => {
    for (let idx = 0; idx < line.stations.length - 1; idx++) {
      const source = line.stations[idx];
      const target = line.stations[idx + 1];
      const sourcePos = nodeLookup[source]?.position;
      const targetPos = nodeLookup[target]?.position;
      const dx = (targetPos?.x ?? 0) - (sourcePos?.x ?? 0);
      const dy = (targetPos?.y ?? 0) - (sourcePos?.y ?? 0);
      const vertical = Math.abs(dy) > Math.abs(dx);
      const sourceHandle =
        vertical && dy < 0
          ? "source-top"
          : vertical && dy >= 0
            ? "source-bottom"
            : dx < 0
              ? "source-left"
              : "source-right";
      const targetHandle =
        vertical && dy < 0
          ? "target-bottom"
          : vertical && dy >= 0
            ? "target-top"
            : dx < 0
              ? "target-right"
              : "target-left";
      edges.push({
        id: `${line.id}-${source}-${target}`,
        source,
        target,
        animated: false,
        style: {
          stroke: line.color,
          strokeWidth: 4,
        },
        sourceHandle,
        targetHandle,
      });
    }
  });

  return edges;
}

export function MetroMapCanvasContents({ map }: { map: MetroMap }) {
  const locationSelectLineId = useMapStore((state) => state.locationSelectLineId);
  const selectedStationId = useMapStore((state) => state.selectedStationId);
  const setSelectedStationId = useMapStore((state) => state.setSelectedStationId);
  const [{ nodes, edges }, setGraph] = useState(() => buildGraph(map, selectedStationId));
  const unselectNodesAndEdges = useReactFlowStore((state) => state.unselectNodesAndEdges);
  const setReactFlow = useMapStore((state) => state.setReactFlow);
  const chatkit = useAppStore((state) => state.chatkit);

  useEffect(() => {
    setGraph(buildGraph(map, selectedStationId));
  }, [map, selectedStationId]);

  // Clear selection whenever location selection mode is toggled
  useEffect(() => {
    setSelectedStationId(null);
    unselectNodesAndEdges();
  }, [locationSelectLineId, unselectNodesAndEdges]);

  useEffect(() => () => setReactFlow(null), [setReactFlow]);

  const onInit = (instance: ReactFlowInstance) => {
    setReactFlow(instance);
    instance.fitView({
      padding: 0.2,
      minZoom: 0.55,
      maxZoom: 1.4,
    });
    const { viewport } = instance.toObject();
    // Add an offset to account for the station label.
    instance.setViewport({ ...viewport, x: viewport.x - 30 });
  };

  const handleSelectionChange = useCallback(
    ({ nodes: selectedNodes = [] }: { nodes?: Node[] }) => {
      const nextSelectedId = selectedNodes[0]?.id ?? null;
      setSelectedStationId(nextSelectedId);
    },
    [setSelectedStationId]
  );

  const handleNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      handleSelectionChange({ nodes: [node] });
      if (!chatkit) return;

      const stationName =
        (node.data as StationNodeData | undefined)?.name ??
        map.stations.find((station) => station.id === node.id)?.name;

      if (!stationName) return;

      chatkit
        .sendUserMessage({ text: `Tell me about ${stationName}` })
        .catch((error) => console.error("Failed to send station prompt.", error));
    },
    [chatkit, handleSelectionChange, map.stations]
  );

  return (
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        onInit={onInit}
        onSelectionChange={handleSelectionChange}
        onNodeClick={handleNodeClick}
        fitView
        minZoom={0.4}
        maxZoom={1.6}
        snapToGrid
        snapGrid={[40, 40]}
        proOptions={{ hideAttribution: true }}
        className="rounded-2xl bg-slate-50 dark:bg-slate-900"
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable
        panOnScroll
        zoomOnDoubleClick={false}
        panOnDrag
      >
        <Background
          id="grid"
          gap={40}
          size={1.5}
          color="rgba(148,163,184,0.5)"
        />
      </ReactFlow>
  );
}

export function MetroMapCanvas(props: { map: MetroMap }) {
  return (
    <ReactFlowProvider>
      <MetroMapCanvasContents {...props} />
    </ReactFlowProvider>
  );
}
