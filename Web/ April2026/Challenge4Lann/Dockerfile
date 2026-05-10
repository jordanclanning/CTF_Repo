FROM php:8.2-alpine
RUN adduser -D -u 1000 chal
RUN apk add --no-cache iputils
WORKDIR /home/chal
COPY index.php flag.txt ./
RUN chmod 444 flag.txt && chown chal:chal index.php flag.txt
USER chal
EXPOSE 80
CMD ["php", "-S", "0.0.0.0:80"]
