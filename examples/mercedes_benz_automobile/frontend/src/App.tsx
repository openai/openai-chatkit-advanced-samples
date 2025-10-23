import { useColorScheme } from "./hooks/useColorScheme";
import Home from "./components/Home";

function App() {
  const { scheme, toggle } = useColorScheme();

  return <Home scheme={scheme} onToggleTheme={toggle} />;
}

export default App;
