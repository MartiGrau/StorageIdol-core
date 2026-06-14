/**
 * @storageidol/mcp-base — public API
 *
 * Every client MCP server should import from this package only:
 *   import { BaseMCPServer, createTool, ok, err } from "@storageidol/mcp-base";
 */

export { BaseMCPServer } from "./server.js";
export type { BaseMCPServerOptions } from "./server.js";

export { createTool } from "./createTool.js";
export type { CompiledTool, ToolDefinition } from "./createTool.js";

export { ok, err } from "./types.js";
export type { ToolResult } from "./types.js";
