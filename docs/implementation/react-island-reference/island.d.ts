export interface IslandHandle {
  update(props: Record<string, unknown>): void;
  unmount(): void;
}

export declare function mountIsland(
  root: Element,
  props?: Record<string, unknown>,
): IslandHandle;

export declare function removalLedger(): string[];
