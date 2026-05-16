import { createApp } from "./app.js";
import { logger } from "./infra/logger/logger.js";

const app = createApp();
const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {

    logger.info(
        {
            port: PORT,
            env: process.env.NODE_ENV || 'development'
        },
        'Server is running and listening for requests'
    )
});