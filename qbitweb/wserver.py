from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig
from time import sleep
from qbittorrentapi import NotFound404Error, Client as qbClient
from aria2p import API as ariaAPI, Client as ariaClient
from flask import Flask, request
from qbitweb.nodes import make_tree

app = Flask(__name__)

aria2 = ariaAPI(ariaClient(host="http://localhost", port=6800, secret=""))

basicConfig(format='[%(levelname)s] [%(filename)s] [%(lineno)d] %(message)s',
                    handlers=[FileHandler("log.txt"), StreamHandler()],
                    level=INFO)

LOGGER = getLogger(__name__)

home = """
<!DOCTYPE html><meta charset=UTF-8><meta content="width=device-width,initial-scale=1"name=viewport><script src=https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js></script><style>body{background-color:#000;height:100vh;font-family:'Source Serif Pro',serif;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center}a{color:#fff}img{max-width:30%;height:auto;display:block;margin-left:auto;margin-right:auto}h2{color:#fff000;margin-top:0}@media (max-width:576px){h2{font-size:32px}img{max-width:70%}}#particles-js{position:absolute;z-index:-1;height:100vh}footer{color:#fff;position:absolute;bottom:0;left:0;right:0;text-align:center}</style><div id=particles-js></div><div><img alt="Culture Cloud"src=https://cdn.jsdelivr.net/gh/culturecloud/static-resources@master/images/cc_transparent_no_outline.png><h2>Your bot is up and running!</h2></div><footer><h6>2021-23 © <a href=https://github.com/culturecloud>Culture Cloud</a></h6></footer><script>particlesJS("particles-js",{particles:{number:{value:250,density:{enable:!0,value_area:800}},color:{value:"#fff000"},shape:{type:"circle",polygon:{nb_sides:5}},opacity:{value:1,random:!1,anim:{enable:!0,speed:15,opacity_min:.1,sync:!0}},size:{value:1,random:!1,anim:{enable:!1,speed:40,size_min:0,sync:!1}},line_linked:{enable:!0,distance:100,color:"#fff000",opacity:1,width:1},move:{enable:!0,speed:3,direction:"none",random:!0,straight:!1,out_mode:"out",bounce:!1,attract:{enable:!1,rotateX:600,rotateY:1200}}},interactivity:{detect_on:"canvas",events:{onhover:{enable:!1,mode:"repulse"},onclick:{enable:!1,mode:"push"},resize:!0},modes:{grab:{distance:400,line_linked:{opacity:1}},bubble:{distance:400,size:40,duration:2,opacity:8,speed:3},repulse:{distance:200,duration:.4},push:{particles_nb:4},remove:{particles_nb:2}}},retina_detect:!0})</script>
"""

page = """
<html lang=en><meta charset=UTF-8><meta content="IE=edge"http-equiv=X-UA-Compatible><meta content="width=device-width,initial-scale=1"name=viewport><title>Torrent File Selector</title><link href=https://telegra.ph/file/43af672249c94053356c7.jpg rel=icon type=image/jpg><script crossorigin=anonymous integrity="sha256-4+XzXVhsDmqanXGHaHvgh1gMQKX40OUvDEBTu8JcmNs="src=https://code.jquery.com/jquery-3.5.1.slim.min.js></script><link href=https://fonts.googleapis.com rel=preconnect><link href=https://fonts.gstatic.com rel=preconnect crossorigin><link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"rel=stylesheet><link href=https://pro.fontawesome.com/releases/v5.10.0/css/all.css rel=stylesheet crossorigin=anonymous integrity=sha384-AYmEC3Yw5cVb3ZcuHtOA93w35dYTsvhLPVnYs9eStHfGJvOvKxVfELGroGkvsg+p><style>*{margin:0;padding:0;box-sizing:border-box;font-family:Ubuntu,sans-serif;list-style:none;text-decoration:none;outline:0!important;color:#fff}body{background-color:#0D1117}header{margin:3vh 1vw;padding:.5rem 1rem .5rem 1rem;display:flex;align-items:center;justify-content:space-between;border-bottom:#161B22;border-radius:30px;background-color:#161B22;border:2px solid rgba(255,255,255,.11)}header:hover,section:hover{box-shadow:0 0 15px #000}.brand{display:flex;align-items:center}img{width:2.5rem;height:2.5rem;border:2px solid #000;border-radius:50%}.name{margin-left:1vw;font-size:1.5rem}.intro{text-align:center;margin-bottom:2vh;margin-top:1vh}.social a{font-size:1.5rem;padding-left:1vw}.brand:hover,.social a:hover{filter:invert(.3)}section{margin:0 1vw;margin-bottom:10vh;padding:1vh 3vw;display:flex;flex-direction:column;border:2px solid rgba(255,255,255,.11);border-radius:20px;background-color:#161B22}li:nth-child(1){padding:1rem 1rem .5rem 1rem}li:nth-child(n+1){padding-left:1rem}li label{padding-left:.5rem}li{padding-bottom:.5rem}span{margin-right:.5rem;cursor:pointer;user-select:none;transition:transform .2s ease-out}span.active{transform:rotate(90deg);-ms-transform:rotate(90deg);-webkit-transform:rotate(90deg);display:inline-block}ul{margin:1vh 1vw 1vh 1vw;padding:0 0 .5rem 0;border:2px solid #000;border-radius:20px;background-color:#1c2129;overflow:hidden}input[type=checkbox]{cursor:pointer;user-select:none}input[type=submit]{border-radius:20px;margin:2vh auto 1vh auto;width:50%;display:block;height:5.5vh;border:2px solid rgba(255,255,255,.11);background-color:#0D1117;font-size:16px;font-weight:500}input[type=submit]:focus,input[type=submit]:hover{background-color:rgba(255,255,255,.068);cursor:pointer}@media (max-width:768px){input[type=submit]{width:100%}}#treeview .parent{position:relative}#treeview .parent>ul{display:none}#sticks{margin:0 1vw;margin-bottom:1vh;padding:1vh 3vw;display:flex;flex-direction:column;border:2px solid rgba(255,255,255,.11);border-radius:20px;background-color:#161b22;align-items:center}#sticks.stick{position:sticky;top:0;z-index:10000}</style><script>function s_validate(){return 0==$("input[name^='filenode_']:checked").length?(alert("Select one file at least!"),!1):void 0}</script><header><div class=brand><img alt=logo src=https://telegra.ph/file/43af672249c94053356c7.jpg><h2 class=name>Bittorrent Selection</h2></div><div class=social><a href=https://github.com/Sam-Max/rclone-mirror-leech-telegram-bot><i class="fa-github fab"></i></a></div></header><div id=sticks><h4>Selected files: <b id=checked_files>0</b> of <b id=total_files>0</b></h4><h4>Selected files size: <b id=checked_size>0</b> of <b id=total_size>0</b></h4></div><section><form action={form_url} method=POST onsubmit="return s_validate()">{My_content} <input name="Select these files ;)"type=submit></form></section><script>$(document).ready(function () {
        docready();
        var tags = $("li").filter(function () {
          return $(this).find("ul").length !== 0;
        });

        tags.each(function () {
          $(this).addClass("parent");
        });

        $("body").find("ul:first-child").attr("id", "treeview");
        $(".parent").prepend("<span>▶</span>");

        $("span").click(function (e) {
          e.stopPropagation();
          e.stopImmediatePropagation();
          $(this).parent( ".parent" ).find(">ul").toggle("slow");
          if ($(this).hasClass("active")) $(this).removeClass("active");
          else $(this).addClass("active");
        });
      });

      if(document.getElementsByTagName("ul").length >= 10){
        var labels = document.querySelectorAll("label");
        //Shorting the file/folder names
        labels.forEach(function (label) {
            if (label.innerText.toString().split(" ").length >= 9) {
                let FirstPart = label.innerText
                    .toString()
                    .split(" ")
                    .slice(0, 5)
                    .join(" ");
                let SecondPart = label.innerText
                    .toString()
                    .split(" ")
                    .splice(-5)
                    .join(" ");
                label.innerText = `${FirstPart}... ${SecondPart}`;
            }
            if (label.innerText.toString().split(".").length >= 9) {
                let first = label.innerText
                    .toString()
                    .split(".")
                    .slice(0, 5)
                    .join(" ");
                let second = label.innerText
                    .toString()
                    .split(".")
                    .splice(-5)
                    .join(".");
                label.innerText = `${first}... ${second}`;
            }
        });
    }</script><script>$('input[type="checkbox"]').change(function(e) {
  var checked = $(this).prop("checked"),
      container = $(this).parent(),
      siblings = container.siblings();
/*
  $(this).attr('value', function(index, attr){
     return attr == 'yes' ? 'noo' : 'yes';
  });
*/
  container.find('input[type="checkbox"]').prop({
    indeterminate: false,
    checked: checked
  });
  function checkSiblings(el) {
    var parent = el.parent().parent(),
        all = true;
    el.siblings().each(function() {
      let returnValue = all = ($(this).children('input[type="checkbox"]').prop("checked") === checked);
      return returnValue;
    });

    if (all && checked) {
      parent.children('input[type="checkbox"]').prop({
        indeterminate: false,
        checked: checked
      });
      checkSiblings(parent);
    } else if (all && !checked) {
      parent.children('input[type="checkbox"]').prop("checked", checked);
      parent.children('input[type="checkbox"]').prop("indeterminate", (parent.find('input[type="checkbox"]:checked').length > 0));
      checkSiblings(parent);
    } else {
      el.parents("li").children('input[type="checkbox"]').prop({
        indeterminate: true,
        checked: false
      });
    }
  }
  checkSiblings(container);
});</script><script>function docready(){$("label[for^='filenode_']").css("cursor","pointer"),$("label[for^='filenode_']").click(function(){$(this).prev().click()}),checked_size(),checkingfiles();var e=$("label[for^='filenode_']").length;$("#total_files").text(e);var i=0,n=$("label[for^='filenode_']");n.each(function(){var e=parseFloat($(this).data("size"));i+=e,$(this).append(" - "+humanFileSize(e))}),$("#total_size").text(humanFileSize(i))}function checked_size(){var e=0,i=$("input[name^='filenode_']:checked");i.each(function(){var i=parseFloat($(this).data("size"));e+=i}),$("#checked_size").text(humanFileSize(e))}function checkingfiles(){var e=$("input[name^='filenode_']:checked").length;$("#checked_files").text(e)}function humanFileSize(e){var i=-1,n=[" kB"," MB"," GB"," TB","PB","EB","ZB","YB"];do e/=1024,i++;while(e>1024);return Math.max(e,0).toFixed(1)+n[i]}function sticking(){var e=$(window).scrollTop(),i=$(".brand").offset().top;e>i?$("#sticks").addClass("stick"):$("#sticks").removeClass("stick")}$("input[name^='foldernode_']").change(function(){checkingfiles(),checked_size()}),$("input[name^='filenode_']").change(function(){checkingfiles(),checked_size()}),$(function(){$(window).scroll(sticking),sticking()})</script>
"""

code_page = """
<html lang=en><meta charset=UTF-8><meta content="IE=edge"http-equiv=X-UA-Compatible><meta content="width=device-width,initial-scale=1"name=viewport><title>Torrent Code Checker</title><link href=https://telegra.ph/file/43af672249c94053356c7.jpg rel=icon type=image/jpg><link href=https://fonts.googleapis.com rel=preconnect><link href=https://fonts.gstatic.com rel=preconnect crossorigin><link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"rel=stylesheet><link href=https://pro.fontawesome.com/releases/v5.10.0/css/all.css rel=stylesheet crossorigin=anonymous integrity=sha384-AYmEC3Yw5cVb3ZcuHtOA93w35dYTsvhLPVnYs9eStHfGJvOvKxVfELGroGkvsg+p><style>*{margin:0;padding:0;box-sizing:border-box;font-family:Ubuntu,sans-serif;list-style:none;text-decoration:none;color:#fff}body{background-color:#0D1117}header{margin:3vh 1vw;padding:.5rem 1rem .5rem 1rem;display:flex;align-items:center;justify-content:space-between;border-bottom:#161B22;border-radius:30px;background-color:#161B22;border:2px solid rgba(255,255,255,.11)}header:hover,section:hover{box-shadow:0 0 15px #000}.brand{display:flex;align-items:center}img{width:2.5rem;height:2.5rem;border:2px solid #000;border-radius:50%}.name{color:#fff;margin-left:1vw;font-size:1.5rem}.intro{text-align:center;margin-bottom:2vh;margin-top:1vh}.social a{font-size:1.5rem;color:#fff;padding-left:1vw}.brand:hover,.social a:hover{filter:invert(.3)}section{margin:0 1vw;margin-bottom:10vh;padding:1vh 3vw;display:flex;flex-direction:column;border:2px solid rgba(255,255,255,.11);border-radius:20px;background-color:#161B22;color:#fff}section form{display:flex;margin-left:auto;margin-right:auto;flex-direction:column}section div{background-color:#0D1117;border-radius:20px;max-width:fit-content;padding:.7rem;margin-top:2vh}section label{font-size:larger;font-weight:500;margin:0 0 .5vh 1.5vw;display:block}section input[type=text]{border-radius:20px;outline:0;width:50vw;height:4vh;padding:1rem;margin:.5vh;border:2px solid rgba(255,255,255,.11);background-color:#3e475531;box-shadow:inset 0 0 10px #000}section input[type=text]:focus{border-color:rgba(255,255,255,.404)}section button{border-radius:20px;margin-top:1vh;width:100%;height:5.5vh;border:2px solid rgba(255,255,255,.11);background-color:#0D1117;color:#fff;font-size:16px;font-weight:500;cursor:pointer;transition:background-color .2s ease}section button:focus,section button:hover{background-color:rgba(255,255,255,.068)}section span{display:block;font-size:x-small;margin:1vh;font-weight:100;font-style:italic;margin-left:23%;margin-right:auto;margin-bottom:2vh}@media (max-width:768px){section form{flex-direction:column;width:90vw}section div{max-width:100%;margin-bottom:1vh}section label{margin-left:3vw;margin-top:1vh}section input[type=text]{width:calc(100% - .3rem)}section button{width:100%;height:5vh;display:block;margin-left:auto;margin-right:auto}section span{margin-left:5%}}</style><header><div class=brand><img alt=logo src=https://telegra.ph/file/43af672249c94053356c7.jpg><h2 class=name>Bittorrent Selection</h2></div><div class=social><a href=https://github.com/Sam-Max/rclone-mirror-leech-telegram-bot><i class="fa-github fab"></i></a></div></header><section><form action={form_url}><div><label for=pin_code>Pin Code :</label><input name=pin_code placeholder="Enter the code that you have got from Telegram to access the Torrent"></div><button class="btn btn-primary"type=submit>Submit</button></form><span>* Dont mess around. Your download will get messed up.</span></section>
"""

def re_verfiy(paused, resumed, client, hash_id):

    paused = paused.strip()
    resumed = resumed.strip()
    if paused:
        paused = paused.split("|")
    if resumed:
        resumed = resumed.split("|")

    k = 0
    while True:
        res = client.torrents_files(torrent_hash=hash_id)
        verify = True
        for i in res:
            if str(i.id) in paused and i.priority != 0:
                verify = False
                break
            if str(i.id) in resumed and i.priority == 0:
                verify = False
                break
        if verify:
            break
        LOGGER.info("Reverification Failed! Correcting stuff...")
        client.auth_log_out()
        sleep(1)
        client = qbClient(host="localhost", port="8090")
        try:
            client.torrents_file_priority(torrent_hash=hash_id, file_ids=paused, priority=0)
        except NotFound404Error:
            raise NotFound404Error
        except Exception as e:
            LOGGER.error(f"{e} Errored in reverification paused!")
        try:
            client.torrents_file_priority(torrent_hash=hash_id, file_ids=resumed, priority=1)
        except NotFound404Error:
            raise NotFound404Error
        except Exception as e:
            LOGGER.error(f"{e} Errored in reverification resumed!")
        k += 1
        if k > 5:
            return False
    LOGGER.info(f"Verified! Hash: {hash_id}")
    return True

@app.route('/app/files/<string:id_>', methods=['GET'])
def list_torrent_contents(id_):

    if "pin_code" not in request.args.keys():
        return code_page.replace("{form_url}", f"/app/files/{id_}")

    pincode = ""
    for nbr in id_:
        if nbr.isdigit():
            pincode += str(nbr)
        if len(pincode) == 4:
            break
    if request.args["pin_code"] != pincode:
        return "<h1>Incorrect pin code</h1>"

    if len(id_) > 20:
        client = qbClient(host="localhost", port="8090")
        res = client.torrents_files(torrent_hash=id_)
        cont = make_tree(res)
        client.auth_log_out()
    else:
        res = aria2.client.get_files(id_)
        cont = make_tree(res, True)
    return page.replace("{My_content}", cont[0]).replace("{form_url}", f"/app/files/{id_}?pin_code={pincode}")

@app.route('/app/files/<string:id_>', methods=['POST'])
def set_priority(id_):

    data = dict(request.form)

    if len(id_) > 20:
        resume = ""
        pause = ""

        for i, value in data.items():
            if "filenode" in i:
                node_no = i.split("_")[-1]

                if value == "on":
                    resume += f"{node_no}|"
                else:
                    pause += f"{node_no}|"

        pause = pause.strip("|")
        resume = resume.strip("|")

        client = qbClient(host="localhost", port="8090")

        try:
            client.torrents_file_priority(torrent_hash=id_, file_ids=pause, priority=0)
        except NotFound404Error:
            raise NotFound404Error
        except Exception as e:
            LOGGER.error(f"{e} Errored in paused")
        try:
            client.torrents_file_priority(torrent_hash=id_, file_ids=resume, priority=1)
        except NotFound404Error:
            raise NotFound404Error
        except Exception as e:
            LOGGER.error(f"{e} Errored in resumed")
        sleep(1)
        if not re_verfiy(pause, resume, client, id_):
            LOGGER.error(f"Verification Failed! Hash: {id_}")
        client.auth_log_out()
    else:
        resume = ""
        for i, value in data.items():
            if "filenode" in i and value == "on":
                node_no = i.split("_")[-1]
                resume += f'{node_no},'

        resume = resume.strip(",")

        res = aria2.client.change_option(id_, {'select-file': resume})
        if res == "OK":
            LOGGER.info(f"Verified! Gid: {id_}")
        else:
            LOGGER.info(f"Verification Failed! Report! Gid: {id_}")
    return list_torrent_contents(id_)

@app.route('/')
def homepage():
    return home

@app.errorhandler(Exception)
def page_not_found(e):
    return f"<h1>404: Torrent not found! Mostly wrong input. <br><br>Error: {e}</h2>", 404

if __name__ == "__main__":
    app.run()

