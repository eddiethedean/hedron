export interface CompositionEdge { id: string; event: string; action: string; target: string; detailKeys?: string[]; maxDepth?: number; maxPayloadBytes?: number; concurrency?: "drop" | "replace" | "queue" | "parallel"; }
export function registerCompositionEdge(edge: CompositionEdge): void;
export function clearCompositionEdges(): void;
export function dispatchComposition(edgeId: string, event: CustomEvent, handlers: object, context?: object): Promise<object>;
export function draftStorageKey(identity: object): string;
export function storeDraft(identity: object, fields: object, options?: object): boolean;
export function consumeDraft(identity: object, options?: object): object | null;
export function clearDrafts(options?: object): void;
export function emitBrowserTrace(trace: object, sink?: (trace: object) => void): boolean;
export function enhanceNavigation(root?: Document | Element): void;
