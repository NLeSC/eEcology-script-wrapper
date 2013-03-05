<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>${self.title()}</title>
<link rel="stylesheet"
    href="${request.static_url('trackertask:static/style.css')}"
    type="text/css"></link>
<link rel="stylesheet"
    href="http://www.uva-bits.nl/wp-content/themes/flysafe/style.css">
<%block name="header"/>
</head>
<body>
    <div id="page">
        <div id="header">
        <a href="http://www.uva-bits.nl/">
            <div id="headerimg"></div>
            </a>
            <div class="menu-header">
                <ul id="menu-hoofdmenu" class="menu">
                    <li id="menu-item-287"
                        class="menu-item menu-item-type-post_type current-menu-item page_item page-item-2 current_page_item menu-item-287"><a
                        href="${request.route_path('index')}"><%block name="title"/></a></li>
                </ul>
            </div>
            <div id="lifewatch">
                <a href="http://www.lifewatch.eu" target="_new"><img
                    src="http://www.uva-bits.nl/wp-content/themes/flysafe/images/lifewatch4.png"
                    id="lifewatch" alt="Lifewatch" /></a>
            </div>
            <div id="uva">
                <a href="http://www.science.uva.nl" target="_new"><img
                    src="http://www.uva-bits.nl/wp-content/themes/flysafe/images/uva4.png"
                    id="uva" alt="UvA" /></a>
            </div>
        </div>
        <div id="content" class="flysafe_content">
            ${self.body()}
        </div>
    </div>
</body>
</html>