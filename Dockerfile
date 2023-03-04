FROM culturecloud/mltb:alpine

WORKDIR /culturecloud/mltb

COPY . .

CMD ["bash", "start.sh"]