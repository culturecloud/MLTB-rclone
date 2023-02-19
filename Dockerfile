FROM culturecloud/mltb:test
    
WORKDIR /culturecloud/mltb
    
COPY . .

ENTRYPOINT ["tini", "--"]
CMD ["bash", "start.sh"]