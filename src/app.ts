import "dotenv/config";
import express, { Application } from "express";

import { WebhookRepository } from "./repositories/WebhookRepository.js";
import { WebhookService } from "./services/WebhookService.js";
import { WebhookController } from "./controllers/WebhookController.js"; 
import { PubSubStrategy } from "./core/strategies/PubSubStrategy.js";
import { BigQueryStrategy } from "./core/strategies/BigQueryStrategy.js";
import { BigQueryRepository } from "./repositories/BigQueryRepository.js";
import { BigQueryService } from "./services/BigQueryService.js";
import { BigQueryController } from "./controllers/BigQueryController.js";
import { requestLogger } from "./infra/logger/requestLogger.middleware.js";
import { webhookAuth } from "./infra/middlewares/webhookAuth.middleware.js";
import { apiAuth } from "./infra/middlewares/apiAuth.middleware.js";

/**
 * Main application file for Sauter Salesforce-WhatsApp API.
 * - Sets up Express app, routes, controllers, services, and repositories.
 * - Configures middleware including JSON parsing and request logging.
 */
export const createApp = (): Application => {
    const app = express();
    app.use(express.json());
    app.use(requestLogger);

    const PushStrategies = [
        new PubSubStrategy,
    ];

    const ReadStrategy = new BigQueryStrategy();

    const repository = new WebhookRepository(PushStrategies);
    const service = new WebhookService(repository);
    const controller = new WebhookController(service);

    app.post("/webhook", 
        webhookAuth,
        controller.receiveWebhook.bind(controller)); 

    const bqRepository = new BigQueryRepository(ReadStrategy);
    const bqService = new BigQueryService(bqRepository);
    const bqController = new BigQueryController(bqService);

    app.get("/salesforce-summaries", 
        apiAuth,
        bqController.get.bind(bqController));
    
    return app;
};