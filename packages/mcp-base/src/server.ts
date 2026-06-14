/**
 * BaseMCPServer — base class for all StorageIdol per-client MCP servers.
 *
 * Usage (in clients/<id>/mcp/index.ts):
 *
 *   import { BaseMCPServer } from "@storageidol/mcp-base";
 *   import { getContact } from "./tools/auth.js";
 *   import { getContracts } from "./tools/contracts.js";
 *
 *   const server = new BaseMCPServer({ clientId: "retras" });
 *   server.registerTool(getContact);
 *   server.registerTool(getContracts);
 *   await server.start();
 *
 * The server listens on stdio (for local MCP) or HTTP (port 3100 in Docker).
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import type { CompiledTool } from "./createTool.js";
import type { ToolResult } from "./types.js";

export interface BaseMCPServerOptions {
  /** The StorageIdol client ID (e.g. "retras"). Used in logs and health checks. */
  clientId: string;
  /** Human-readable name for this MCP server. Defaults to "storageidol-mcp-<clientId>". */
  name?: string;
  version?: string;
}

export class BaseMCPServer {
  private readonly _clientId: string;
  private readonly _server: Server;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private readonly _tools = new Map<string, CompiledTool<any, any>>();

  constructor(options: BaseMCPServerOptions) {
    this._clientId = options.clientId;
    const name = options.name ?? `storageidol-mcp-${options.clientId}`;
    const version = options.version ?? "0.1.0";

    this._server = new Server(
      { name, version },
      { capabilities: { tools: {} } }
    );

    this._registerHandlers();
  }

  /** Register a compiled tool (created via createTool). */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  registerTool(tool: CompiledTool<any, any>): this {
    if (this._tools.has(tool.definition.name)) {
      throw new Error(
        `Tool "${tool.definition.name}" already registered on client "${this._clientId}"`
      );
    }
    this._tools.set(tool.definition.name, tool);
    return this;
  }

  /** Start serving on stdio transport. */
  async start(): Promise<void> {
    const transport = new StdioServerTransport();
    await this._server.connect(transport);
    console.error(
      `[${this._clientId}] MCP server started with ${this._tools.size} tools: ${[...this._tools.keys()].join(", ")}`
    );
  }

  private _registerHandlers(): void {
    // List tools
    this._server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools = [...this._tools.values()].map((t) => ({
        name: t.mcpDescriptor.name,
        description: t.mcpDescriptor.description,
        inputSchema: t.mcpDescriptor.inputSchema,
      }));
      return { tools };
    });

    // Call tool
    this._server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      const tool = this._tools.get(name);

      if (!tool) {
        return {
          isError: true,
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                ok: false,
                error: `Unknown tool: ${name}`,
                code: "UNKNOWN_TOOL",
              }),
            },
          ],
        };
      }

      const result: ToolResult = await tool.call(args ?? {});

      return {
        isError: !result.ok,
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(result),
          },
        ],
      };
    });
  }
}
