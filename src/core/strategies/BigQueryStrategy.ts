import { bigQueryClient  } from '../../infra/singleton/bigquery.js';
import { BaseReadStrategy } from './BaseReadStrategy.js';
import { Logger } from 'pino';

/**
 * Read strategy that retrieves messages from a BigQuery table.
 *
 * - Builds and executes a paginated SELECT query against the configured dataset/table.
 * - Executes a COUNT query to determine the total number of rows available.
 * - Logs duration and row counts for monitoring and performance analysis.
 *
 * Environment variables required:
 * - `BQ_DATASET` - BigQuery dataset ID
 * - `BQ_TABLE` - BigQuery table name
 */
export class BigQueryStrategy implements BaseReadStrategy {
    private datasetId = process.env.BQ_DATASET!;
    private tableId = process.env.BQ_TABLE!;

    /**
     * Query BigQuery for a specific page of results.
     *
     * @param params.page - 1-based page number to retrieve
     * @param params.limit - Number of items per page
     * @param log - Pino logger for instrumentation and error reporting
     * @returns An object with `data` (rows) and `total` (total rows available)
     * @throws Propagates any errors thrown by the BigQuery client
     */
    async find({ page, limit }: { page: number; limit: number }, log: Logger): Promise<{ data: any[]; total: number }> {
        const offset = (page - 1) * limit;

        const query = `
            SELECT *
            FROM \`${this.datasetId}.${this.tableId}\`
            ORDER BY criado_em DESC
            LIMIT ${limit}
            OFFSET ${offset}
        `;

        const totalQuery = `
            SELECT COUNT(*) as total
            FROM \`${this.datasetId}.${this.tableId}\`
        `;

        const start = Date.now();
        try {
            const [rows] = await bigQueryClient.query(query);
            const [totalRows] = await bigQueryClient.query(totalQuery);

            log.info(
                { duration: Date.now() - start, rows: rows.length },
                'BigQuery find operation completed'
            );

            return {
                data: rows,
                total: Number(totalRows[0].total ?? 0)
            };
        } catch (error: any) {
            log.error(
                { err: error, durationMs: Date.now() - start },
                'BigQuery find operation failed'
            );
            throw error;
        }
    }
}