import { PubSub } from '@google-cloud/pubsub';

class PubSubSingleton {
    private static instance: PubSub;

    static getInstance(): PubSub {
        if (!this.instance) {
            this.instance = new PubSub({
                projectId: process.env.GCP_PROJECT_ID,
            });
        }
        return this.instance;
    }
}

export const pubsubClient = PubSubSingleton.getInstance();