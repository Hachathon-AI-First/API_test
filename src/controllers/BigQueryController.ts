import { BigQueryService } from "../services/BigQueryService.js";

/**
 * Controller exposing HTTP endpoints for BigQuery-related operations.
 *
 * This controller translates HTTP requests into service calls, handles
 * parameter parsing (page & limit), performs basic logging, and converts
 * service results into JSON HTTP responses.
 *
 * Example usage (express):
 * const controller = new BigQueryController(service);
 * app.get('/messages', (req, res) => controller.get(req, res));
 */
export class BigQueryController {
    private service: BigQueryService;

    constructor(service: BigQueryService) {
        this.service = service;
    }

    /**
     * Handle GET /messages (or similar) to return paginated BigQuery results.
     *
     * - Reads `page` and `limit` from `req.query`, applying sensible defaults.
     * - Logs the incoming request and delegates to `BigQueryService.fetchMessages`.
     * - On success, returns HTTP 200 with the service result as JSON.
     * - On failure, logs the error and returns HTTP 500 with the error message.
     *
     * @param req - Express request-like object. Expects `req.query` and `req.log`.
     * @param res - Express response-like object used to send JSON responses.
     */
    async get(req: any, res: any): Promise<void> {
        const page = Number(req.query.page ?? 1);
        const limit = Number(req.query.limit ?? 20);

        req.log.info(`Fetching BigQuery messages - Page: ${page}, Limit: ${limit}`);

        try {
            const result = await this.service.fetchData(page, limit, req.log);
            res.status(200).json(result);
        } catch (error: any) {
            req.log.error({ err: error }, 'Error fetching BigQuery messages');
            res.status(500).json({ error: error.message });
        }
    };
}