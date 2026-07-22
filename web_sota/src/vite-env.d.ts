/// <reference types="vite/client" />

declare module "butterchurn" {
  const createVisualizer: (canvas: HTMLCanvasElement, opts: Record<string, any>) => any;
  const butterchurn: { createVisualizer: typeof createVisualizer };
  export default butterchurn;
}

declare module "butterchurn-presets" {
  const presets: Record<string, any>;
  export default presets;
}
