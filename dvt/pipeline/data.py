# -*- coding: utf-8 -*-
"""Web scripts stored as text files
"""

INDEX_MAIN = """
<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8">
    <title>DVT Visualization</title>

    <!-- CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <link href="css/dvt.css" rel="stylesheet">

    </head>
    <body>

  <main role="main" class="container">

    <div class="starter-template">
      <h1>Distant Viewing Toolkit &mdash; Video Visualization</h1>
    </div>

    <div style="text-align: left; padding: 2rem 4rem">
    <p class="lead">
    Below are available videos that have been annotated. Click on the
    thumbnail to see extracted frames from each object. This page has been
    automatically generated by the
    <a href="https://github.com/distant-viewing/dvt" target="_blank"
    rel="noopener noreferrer">distant viewing toolkit</a>.
    </p>
    </div>

    <div style="text-align: left; padding: 2rem 10rem" id="help">
    <p class="lead">
    <h2>Loading...</h2>
    </p>
    <p class="lead">
    Note: If you are seeing this text in place of the list of videos,
    then the javascript code is not running properly. You most likely
    not running the page using a local webserver. See the
    <a href="https://github.com/distant-viewing/dvt" target="_blank"
    rel="noopener noreferrer">README.md file on GitHub</a> for details of
    how to do this using Python.</h3>
    </p>
    </div>

    <div class="row" id="container">
      <div class="col-md-6" id="template" style="display: none;">
        <div class="thumbnail">
          <a href="" target="_blank" rel="noopener noreferrer">
            <img src="" alt="..." style="width:100%">
            <div class="caption" style="">
              <p style="font-size: 24px; color: black"></p>
            </div>
          </a>
        </div>
      </div>
    </div>


  </main><!-- /.container -->

  <!-- javascript -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
    <script src="js/dvt-main.js"></script>
    </body>
</html>
"""

INDEX_PAGE = """
<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8">
    <title>DVT Visualization</title>

    <!-- CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <link href="../css/dvt.css" rel="stylesheet">

    </head>
    <body>

  <main role="main" class="container" id="container">

    <div class="starter-template">
      <h1>Distant Viewing Toolkit &mdash; Video Visualization</h1>
    </div>

        <div style="text-align: left; padding: 2rem 4rem">
            <p class="lead">
                This is the default visualization of extracted metadata using the
                distant viewing toolkit. The objective of the visualization is to
                demonstrate how computer vision can be used as a <i>way of seeing</i>
                the visual material. Below are selected frames from the input video
                file.  The first frame shows detected objets and people; the second
                frame illustrates movement (hue is direction and saturation is speed)
                using optical flow. Other extracted fields are shown on the right.
                See the <a href="https://distantviewing.org" target="_blank"
                rel="noopener noreferrer">distant viewing project</a>
                page for further information.
            </p>
        </div>

    <div style="text-align: left; padding: 2rem 10rem" id="help">
    <p class="lead">
    <h2>Loading...</h2>
    </p>
    <p class="lead">
    Note: If you are seeing this text in place of the frames after the page
    finishes loading, this means
    than the javascript code is not running properly. You most likely
    not running the page using a local webserver. See the
    <a href="https://github.com/distant-viewing/dvt" target="_blank"
    rel="noopener noreferrer">README.md file on GitHub</a> for details of
    how to do this using Python.</h3>
    </p>
    </div>

    <div class="media" id="frame-default" style="display: none;">
        <span class="media-left">
    <img class="frame-img" src="" alt="..." id="">
    <img class="frame-img" src="" alt="..." id="">
        </span>
        <div class="media-body">
            <ul>
              <li><b>Time start:</b> <span></span></li>
              <li><b>Time end:</b> <span></span></li>
              <li><b>Number of faces:</b> <span></span></li>
              <li><b>Number of people:</b> <span></span></li>
    <li><b>Objects:</b> <span></span></li>
    <li><b>Shot length:</b> <span></span></li>
            </ul>
        </div>
    </div>

  </main><!-- /.container -->

  <!-- javascript -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
  <script type="text/javascript" src="../js/dvt.js"></script>

    </body>
</html>
"""

DVT_CSS = """
body {
  padding-top: 0rem;
}

.media {
  padding: 1rem 1rem;
  margin: 12px;
  border-radius: 5px;
  border: 2px solid #ccc;
  color: #555;
  width:1100px;
  background-color: #eeeeee;
}

.media-body {
    padding: 1rem;
}

.frame-img {
  height:250px;
}
"""

DVT_JS = """
var oReq = new XMLHttpRequest();

oReq.onreadystatechange = function () {
    var DONE = this.DONE || 4;
    if (this.readyState === DONE){
        var jsonObj = JSON.parse(this.responseText);

        var container = document.getElementById("container");
        var frame_info = document.getElementById("frame-default");

        for(var i = 0; i < jsonObj.length; i++) {
          var cln = frame_info.cloneNode(true);
          cln.style = "";

          cln.children[0].children[0].src = jsonObj[i]['anno_path'];
          cln.children[0].children[1].src = jsonObj[i]['flow_path'];
          cln.children[0].children[0].id = 'img' + (i).toString();
          ulist = cln.children[1].children[0].children
          ulist[0].children[1].textContent = jsonObj[i]['time_start'];
          ulist[1].children[1].textContent = jsonObj[i]['time_end'];
          ulist[2].children[1].textContent = jsonObj[i]['num_faces'].toString();
          ulist[3].children[1].textContent = jsonObj[i]['num_people'].toString();
          ulist[4].children[1].textContent = jsonObj[i]['obj_list'];
          ulist[5].children[1].textContent = jsonObj[i]['shot_length'];

          container.appendChild(cln);
        }

        document.getElementById("help").style = "display: none;";

    }
};

oReq.open("GET", "data.json");
oReq.send(null);
"""

DVT_MAIN_JS = """

var oReq = new XMLHttpRequest();

oReq.onreadystatechange = function () {
    var DONE = this.DONE || 4;
    if (this.readyState === DONE){
        var jsonObj = JSON.parse(this.responseText);

        var container = document.getElementById("container");
        var image_template = document.getElementById("template");

        for(var i = 0; i < jsonObj.length; i++) {
          var cln = image_template.cloneNode(true);
          cln.style = "";

          link_elem = cln.children[0].children[0];
          link_elem.href = jsonObj[i]['video_name'];
          link_elem.children[0].src = jsonObj[i]['thumb_path'];
          link_elem.children[1].children[0].textContent = jsonObj[i]['video_name'];

          container.appendChild(cln);
        }

        document.getElementById("help").style = "display: none;";

    }
};

oReq.open("GET", "toc.json");
oReq.send(null);
"""