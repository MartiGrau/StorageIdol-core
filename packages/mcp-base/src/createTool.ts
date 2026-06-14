/**
 * createTool — factory for MCP tools with Zod validation and structured errors.
 *
 * Usage:
 *   const getContact = createTool({
 *     name: "get_contact",
 *     description: "Retrieve a contact from the CRM by phone number.",
 *     inputSchema: z.object({ phone: z.string().min(9) }),
 *     handler: async ({ phone }) => {
 *       const data = await crm.getByPhone(phone);
 *       if (!data) return err("NOT_FOUND", `No contact for phone ${phone}`);
 *       return ok(data);
 *     },
 *   });
 *
 * Rules:
 *   - The handler must NEVER throw to the agent.
 *   - Always return ok(data) on success, err(code, message) on failure.
 *   - Input is Zod-validated before the handler is called.
 *   - error codes are SCREAMING_SNAKE_CASE identifiers (NOT HTTP status codes).
 */

import { z } from "zod";
import { err, type ToolDefinition, type ToolResult } from "./types.js";

export interface CompiledTool<TInput extends z.ZodTypeAny, TOutput = unknown> {
  definition: ToolDefinition<TInput, TOutput>;
  /** Call the tool with raw (unvalidated) input. Returns a ToolResult. */
  call: (rawInput: unknown) => Promise<ToolResult<TOutput>>;
  /** MCP-compatible tool descriptor for server registration. */
  mcpDescriptor: {
    name: string;
    description: string;
    inputSchema: Record<string, unknown>;
  };
}

export function createTool<TInput extends z.ZodTypeAny, TOutput = unknown>(
  definition: ToolDefinition<TInput, TOutput>
): CompiledTool<TInput, TOutput> {
  const call = async (rawInput: unknown): Promise<ToolResult<TOutput>> => {
    // Zod validation
    const parsed = definition.inputSchema.safeParse(rawInput);
    if (!parsed.success) {
      const details = parsed.error.issues
        .map((i) => `${i.path.join(".")}: ${i.message}`)
        .join("; ");
      return err("VALIDATION_ERROR", `Invalid input: ${details}`);
    }

    // Handler invocation — catch all exceptions
    try {
      return await definition.handler(parsed.data as z.infer<TInput>);
    } catch (thrown: unknown) {
      const message =
        thrown instanceof Error ? thrown.message : String(thrown);
      console.error(
        `[mcp-base] Tool "${definition.name}" threw unexpectedly: ${message}`,
        thrown
      );
      return err("INTERNAL_ERROR", `Tool ${definition.name} failed: ${message}`);
    }
  };

  // Convert Zod schema to JSON Schema for MCP descriptor
  // This is a simplified conversion — for complex schemas use zod-to-json-schema.
  const inputSchema = zodToJsonSchema(definition.inputSchema);

  return {
    definition,
    call,
    mcpDescriptor: {
      name: definition.name,
      description: definition.description,
      inputSchema,
    },
  };
}

/** Minimal Zod → JSON Schema converter for tool registration. */
function zodToJsonSchema(schema: z.ZodTypeAny): Record<string, unknown> {
  if (schema instanceof z.ZodObject) {
    const shape = schema.shape as Record<string, z.ZodTypeAny>;
    const properties: Record<string, unknown> = {};
    const required: string[] = [];
    for (const [key, val] of Object.entries(shape)) {
      properties[key] = zodTypeToJsonSchema(val);
      if (!(val instanceof z.ZodOptional)) required.push(key);
    }
    return { type: "object", properties, required };
  }
  return zodTypeToJsonSchema(schema);
}

function zodTypeToJsonSchema(schema: z.ZodTypeAny): Record<string, unknown> {
  if (schema instanceof z.ZodString) return { type: "string" };
  if (schema instanceof z.ZodNumber) return { type: "number" };
  if (schema instanceof z.ZodBoolean) return { type: "boolean" };
  if (schema instanceof z.ZodArray)
    return { type: "array", items: zodTypeToJsonSchema(schema.element) };
  if (schema instanceof z.ZodOptional)
    return zodTypeToJsonSchema(schema.unwrap());
  if (schema instanceof z.ZodNullable)
    return { ...zodTypeToJsonSchema(schema.unwrap()), nullable: true };
  if (schema instanceof z.ZodEnum) return { type: "string", enum: schema.options };
  if (schema instanceof z.ZodObject) return zodToJsonSchema(schema);
  // Fallback
  return { type: "string" };
}
