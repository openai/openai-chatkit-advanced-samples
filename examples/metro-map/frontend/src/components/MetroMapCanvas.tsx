import { useEffect, useState } from "react";
import ReactFlow, {
  Background,
  Handle,
  Position,
  ReactFlowProvider,
  applyNodeChanges,
  type Edge,
  type Node,
  type NodeChange,
  type NodeProps,
  type ReactFlowInstance,
} from "reactflow";

import { X_UNIT, Y_UNIT, type Line, type MetroMap, type Station } from "../lib/map";
import { useMapStore } from "../store/useMapStore";

type MetroMapCanvasProps = {
  map: MetroMap;
};

type StationNodeData = Station & {
  isFirst: boolean;
  isLast: boolean;
  lineColors: Record<string, string>;
};

const NODE_TYPES = {
  station: StationNode,
};

function StationNode({ data }: NodeProps<StationNodeData>) {
  const { name, lines, lineColors } = data;
  const dotColors = lines
    .map((lineId) => lineColors[lineId])
    .filter((color): color is string => Boolean(color));
  const primaryColor = dotColors[0] ?? "#0ea5e9";
  const isExchange = dotColors.length > 1;
  return (
    <div className="relative flex flex-col items-center">
      {/* Hidden handles on all sides so edges can connect based on orientation. */}
      <Handle id="target-left" type="target" position={Position.Left} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="target-right" type="target" position={Position.Right} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="target-top" type="target" position={Position.Top} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="target-bottom" type="target" position={Position.Bottom} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-left" type="source" position={Position.Left} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-right" type="source" position={Position.Right} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-top" type="source" position={Position.Top} className="!h-0 !w-0 !bg-transparent !border-0" />
      <Handle id="source-bottom" type="source" position={Position.Bottom} className="!h-0 !w-0 !bg-transparent !border-0" />

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

function buildGraph(map: MetroMap): { nodes: Node[]; edges: Edge[] } {
  const nodes = buildNodes(map);
  const edges = buildEdges(map, nodes);
  return { nodes, edges };
}

function buildNodes(map: MetroMap): Node<StationNodeData>[] {
  const lineColor: Record<string, string> = {};
  map.lines.forEach((line) => {
    lineColor[line.id] = line.color;
  });

  return map.stations.map((station) => {
    const isFirst = !!map.lines
      .filter((line) => line.stations.includes(station.id))
      .find((line) => line.stations.indexOf(station.id) === 0)
    const isLast = !!map.lines
      .filter((line) => line.stations.includes(station.id))
      .find((line) => line.stations.indexOf(station.id) === line.stations.length - 1)
    return {
      id: station.id,
      type: "station",
      position: { x: station.x * X_UNIT, y: station.y * Y_UNIT },
      data: {
        ...station,
        isFirst,
        isLast,
        lineColors: lineColor,
      },
      draggable: true,
      selectable: true,
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

function MetroFlow({ map }: { map: MetroMap }) {
  const [{ nodes, edges }, setGraph] = useState(() => buildGraph(map));
  const setReactFlow = useMapStore((state) => state.setReactFlow);

  useEffect(() => {
    setGraph(buildGraph(map));
  }, [map]);

  useEffect(() => () => setReactFlow(null), [setReactFlow]);

  const onInit = (instance: ReactFlowInstance) => {
    setReactFlow(instance);
    instance.fitView({
      padding: 0.2,
      minZoom: 0.55,
      maxZoom: 1.4,
      includeHiddenNodes: true,
    });
  };

  const onNodesChange = (changes: NodeChange[]) => {
    setGraph((prev) => {
      const nextNodes = applyNodeChanges(changes, prev.nodes);
      return {
        nodes: nextNodes,
        edges: buildEdges(map, nextNodes),
      };
    });
  };

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={NODE_TYPES}
      onInit={onInit}
      onNodesChange={onNodesChange}
      fitView
      minZoom={0.4}
      maxZoom={1.6}
      snapToGrid
      snapGrid={[40, 40]}
      proOptions={{ hideAttribution: true }}
      className="rounded-2xl bg-slate-50 dark:bg-slate-900"
      nodesDraggable
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

export function MetroMapCanvas({ map }: MetroMapCanvasProps) {
  return (
    <ReactFlowProvider>
      <MetroFlow map={map} />
    </ReactFlowProvider>
  );
}
