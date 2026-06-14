/**
 * Shared types for StorageIdol MCP servers.
 *
 * Every client MCP extends BaseMCPServer and registers tools via createTool.
 * Tools always return a ToolResult — never throw to the agent.
 */

import { z } from "zod";

/** Every tool result is either success+data or a structured error. */
export type ToolResult<T = unknown> =
  | { ok: true; data: T }
  | { ok: false; error: string; code: string };

/** Convenience helper to construct a success result. */
export function ok<T>(data: T): ToolResult<T> {
  return { ok: true, data };
}

/** Convenience helper to construct a structured error result. */
export function err(code: string, error: string): ToolResult<never> {
  return { ok: false, error, code };
}

/** Zod schema for the tool result envelope (used in tests). */
export const ToolResultSchema = z.discriminatedUnion("ok", [
  z.object({ ok: z.literal(true), data: z.unknown() }),
  z.object({ ok: z.literal(false), error: z.string(), code: z.string() }),
]);

/** Tool definition passed to createTool. */
export interface ToolDefinition<
  TInput extends z.ZodTypeAny,
  TOutput = unknown,
> {
  /** Name shown to the LLM. Use snake_case. Max 64 chars. */
  name: string;
  /** Clear, concise description for the LLM. Explain WHEN to use this tool. */
  description: string;
  /** Zod schema for input validation. */
  inputSchema: TInput;
  /** Implementation. Must never throw — catch errors and return err(). */
  handler: (input: z.infer<TInput>) => Promise<ToolResult<TOutput>>;
}
