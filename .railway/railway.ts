import { defineSchema, Schema } from "@railwayapp/cli";
export default defineSchema(() => ({
  $schema: "https://cdn.railway.app/railway.schema.json",
  build: { dockerfile: "Dockerfile" },
  deploy: {
    startCommand: "python -m uvicorn main:app --host 0.0.0.0 --port 8000",
    port: 8000,
    healthcheckPath: "/health",
    healthcheckInterval: 10,
    healthcheckTimeout: 5,
    healthcheckRetries: 3,
  },
  services: {
    "agentic-ai-course": {
      build: { dockerfile: "Dockerfile" },
      deploy: {
        startCommand: "python -m uvicorn main:app --host 0.0.0.0 --port 8000",
        port: 8000,
      },
    },
  },
}));
