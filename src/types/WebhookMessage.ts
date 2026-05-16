export interface WebhookMessage {
    origem: string;
    destino: string;
    pushName: string;
    mensagem: string;
    status: string;
    created_at: string;
    event?: string;
}