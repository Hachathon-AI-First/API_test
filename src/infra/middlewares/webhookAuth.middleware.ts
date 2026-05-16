import { Request, Response, NextFunction } from 'express';

export function webhookAuth(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const log = (req as any).log;

  const rawToken = req.query.token;
  const envSecret = process.env.WEBHOOK_SECRET;

  if (typeof rawToken !== 'string') {
    log.warn('Webhook auth failed: token missing or not string');
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!envSecret) {
    log.error('WEBHOOK_SECRET not set');
    return res.status(500).json({ error: 'Server misconfigured' });
  }

  const token = decodeURIComponent(rawToken).trim();
  const secret = envSecret.trim();

  log.info(
    {
      receivedTokenLength: token.length,
      expectedTokenLength: secret.length,
      equals: token === secret,
    },
    'Webhook auth token comparison'
  );

  if (token !== secret) {
    log.warn('Webhook auth failed: invalid token');
    return res.status(401).json({ error: 'Unauthorized' });
  }

  log.info('Webhook auth successful');
  next();
}
