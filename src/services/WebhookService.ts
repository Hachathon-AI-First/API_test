import { WebhookRepository } from '../repositories/WebhookRepository.js';
import { WebhookMessage } from '../types/WebhookMessage.js';
import { Logger } from 'pino';
/**
 * Service responsible for validating and normalizing incoming webhook payloads,
 * then delegating persistence to the provided WebhookRepository.
 *
 * Example usage:
 * const svc = new WebhookService(repo);
 * await svc.processWebhook(payload, logger);
 */
export class WebhookService {
    private repository: WebhookRepository;

    /**
     * Create a new WebhookService.
     * @param repository - Repository used to persist processed webhook messages.
     */
    constructor(repository: WebhookRepository) {
        this.repository = repository;
    }

    /**
     * Normalize an incoming webhook payload and persist it using the repository.
     *
     * - Extracts expected fields from raw `data`.
     * - Fills missing `pushName` with an empty string and `created_at` with current ISO timestamp.
     * - Delegates persistence to `repository.saveMessage`.
     *
     * @param data - Raw webhook payload (may be partial or unvalidated).
     * @param log - Pino logger instance used by the repository for logging.
     * @returns The result returned by `repository.saveMessage` (implementation specific).
     */
    async processWebhook(data: any, log: Logger): Promise<any> {
        
        const cleanData: WebhookMessage = {
            
            event: data.event, 
            origem: data.origem,
            destino: data.destino,
            pushName: data.pushName || "",
            mensagem: data.mensagem,
            status: data.status,
            created_at: data.created_at || new Date().toISOString() 
        };

        /* send processed data to repository */
        return this.repository.saveMessage(cleanData, log);
    }
}