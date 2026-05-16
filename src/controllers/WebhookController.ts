import { Request, Response } from 'express';
import { WebhookService } from '../services/WebhookService.js'; 

/**
 * Controller responsible for receiving incoming webhook HTTP requests and
 * delegating processing to the `WebhookService`.
 *
 * The controller expects an Express-like `req` with `req.body` containing
 * the webhook payload and `req.log` (a Pino logger) attached by middleware.
 *
 * Example (Express):
 * const controller = new WebhookController(service);
 * app.post('/webhook', controller.receiveWebhook);
 */
export class WebhookController {
    private service: WebhookService; 

    constructor(service: WebhookService) {
        this.service = service;
    }

    /**
     * Express handler that receives a webhook payload and forwards it to the service.
     *
     * - Expects `req.body` to include the raw webhook payload and `req.log` to be present.
     * - On success, responds with HTTP 200 and an object containing the `messageId` returned by the service.
     * - On failure, logs the error and responds with HTTP 500 and the error message.
     *
     * @param req - Express request-like object. Should include `body` and `log`.
     * @param res - Express response-like object used to send JSON responses.
     */
    receiveWebhook = async (req: any, res: any): Promise<void> => {
        try {
            const result = await this.service.processWebhook(req.body, req.log);
            res.status(200).json({ messageId: result });
        } catch (error: any) {
            req.log.error({ err: error }, 'Error processing webhook');
            res.status(500).json({ error: error.message });
        }
    };
}