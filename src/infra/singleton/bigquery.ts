import { BigQuery } from '@google-cloud/bigquery';

class BigQuerySingleton {
    private static instance: BigQuery;

    static getInstance(): BigQuery {
        if (!this.instance) {
            this.instance = new BigQuery({
                projectId: process.env.GCP_PROJECT_ID,
                });
        }
        return this.instance;
    }
}

export const bigQueryClient = BigQuerySingleton.getInstance();