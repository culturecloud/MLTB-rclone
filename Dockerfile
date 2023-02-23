FROM culturecloud/mltb:sam-max
    
WORKDIR /culturecloud/mltb
    
COPY . .

CMD ["bash", "start.sh"]