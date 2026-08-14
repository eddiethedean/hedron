export declare function track(el: Element, resources?: { listener?: unknown; timer?: number }): AbortSignal;
export declare function dispose(el: Element): void;
export declare function validateEventDetail(
  detail: unknown,
  schemaKeys?: string[],
): boolean;
