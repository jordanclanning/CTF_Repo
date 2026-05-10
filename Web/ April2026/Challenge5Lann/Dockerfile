FROM php:8.2-alpine
RUN apk add --no-cache sqlite
RUN adduser -D -u 1000 chal
WORKDIR /home/chal
COPY index.html login.php style.css airport.jpg init.sql ./
RUN mkdir -p assets/images && \
    mv airport.jpg assets/images/ && \
    sqlite3 database.db < init.sql && \
    chmod 444 database.db init.sql && \
    chown chal:chal *.html *.php *.css database.db init.sql && \
    chown -R chal:chal assets/
USER chal
EXPOSE 80
CMD ["php", "-S", "0.0.0.0:80"]
