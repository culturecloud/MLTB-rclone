FROM culturecloud/mltb:sam-max
    
WORKDIR /culturecloud/mltb
    
COPY . .

ENTRYPOINT ["tini", "--"]
CMD ["bash", "start.sh"]