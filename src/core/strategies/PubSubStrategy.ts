import { pubsubClient } from '../../infra/singleton/pubsub.js';
import { BaseStrategy } from './BaseStrategy.js';
import { WebhookMessage } from '../../types/WebhookMessage.js';
import { Logger } from 'pino';

/**
 * Strategy that publishes webhook messages to Google Cloud Pub/Sub.
 *
 * Responsibilities:
 * - Ensure the configured topic exists (create it if necessary).
 * - Serialize the `WebhookMessage` payload and publish it to the topic.
 * - Log timing and success/failure details via the provided logger.
 *
 * This strategy returns a simple `{ published: boolean }` result to indicate
 * successful publication. Errors from the Pub/Sub client are propagated to callers.
 */
export class PubSubStrategy implements BaseStrategy {

    private get topicNameOrId(): string {
        const topic = process.env.PUBSUB_TOPIC;
        if (!topic) {
        throw new Error('PUBSUB_TOPIC environment variable is not set.');
        }

        return topic;
    }



    /**
     * Ensure the configured Pub/Sub topic exists. If not, create it.
     *
     * @throws Any error raised by the Pub/Sub client when fetching or creating topics.
     */
    async createTopicIfNotExists(): Promise<void> {
        const [topics] = await pubsubClient.getTopics();
        const topicExists = topics.some(topic => topic.name.endsWith(this.topicNameOrId));

        if (!topicExists) {
            await pubsubClient.createTopic(this.topicNameOrId);
        } 
    }

    /**
     * Publish a `WebhookMessage` to the configured Pub/Sub topic.
     *
     * - Calls `createTopicIfNotExists` to ensure the topic is available.
     * - Serializes the message to JSON and publishes it as a message buffer.
     * - Logs duration and metadata on success, and logs error details on failure.
     *
     * @param message - Normalized webhook message to publish.
     * @param log - Pino logger instance for instrumentation and error reporting.
     * @returns An object indicating whether the message was published: `{ published: true }` on success.
     * @throws Propagates errors thrown by the Pub/Sub client.
     */
    async publish(message: WebhookMessage, log: Logger): Promise<{ published: boolean}> {
        const start = Date.now();

        try {
            await this.createTopicIfNotExists();
            const dataBuffer = Buffer.from(JSON.stringify(message));
            await pubsubClient.topic(this.topicNameOrId).publishMessage({ data: dataBuffer });

            log.info(
                {
                    topic: this.topicNameOrId,
                    durationMs: Date.now() - start,
                    message: message
                },
                'Message published to Pub/Sub successfully'
            );
            return { published: true };
        } catch (error) {
            log.error(
                {
                    topic: this.topicNameOrId,
                    err: error,
                    durationMs: Date.now() - start,              
                },
                'Failed to publish message to Pub/Sub'
            );
            throw error;
        }
    }
}