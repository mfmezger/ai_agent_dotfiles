# Runtime Validation, Errors, and Async

## Trust Boundaries

- Treat network responses, environment variables, local storage, file contents, and user input as `unknown`.
- Validate external data before it becomes domain data.
- Prefer schema-based parsing with the project's existing validation library. If the repo has no established choice, Zod is a reasonable default.

```ts
import { z } from "zod";

const ConfigSchema = z.object({
  port: z.number().int().positive(),
  env: z.enum(["dev", "test", "prod"]),
});

type Config = z.infer<typeof ConfigSchema>;

export function parseConfig(input: unknown): Config {
  return ConfigSchema.parse(input);
}
```

## Errors

- Throw at boundaries when the framework expects exceptions.
- Return typed results or domain-specific errors in core logic when callers need branching behavior.
- Include actionable context in messages. Name the operation, field, or identifier that failed.

## Async

- Always await or intentionally detach promises with an explicit comment or utility.
- Avoid hidden concurrency. If multiple operations can run in parallel, express that explicitly with `Promise.all` or `Promise.allSettled`.
- Model cancellation where the platform supports it, typically with `AbortSignal`.

```ts
export async function loadUser(id: string, signal?: AbortSignal): Promise<User> {
  const response = await fetch(`/api/users/${id}`, { signal });
  if (!response.ok) throw new Error(`failed to load user ${id}`);
  return UserSchema.parse(await response.json());
}
```

## Promise Hygiene

- Avoid `Array.prototype.forEach(async ...)`.
- Avoid swallowing rejections.
- Avoid returning `Promise<any>` or `Promise<unknown>` from stable APIs unless that uncertainty is the point.

## Review Heuristics

- If external data enters the system without validation, the boundary is wrong.
- If async work can fail silently, the control flow is wrong.
- If error messages omit the failing operation or identifier, diagnostics are weak.
