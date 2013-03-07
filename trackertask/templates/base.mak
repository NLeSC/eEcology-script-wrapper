<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script Wrapper - ${self.title()}</title>
<link rel="stylesheet"
    href="${request.static_url('trackertask:static/style.css')}"
    type="text/css"></link>
<link rel="stylesheet"
    href="http://www.uva-bits.nl/wp-content/themes/flysafe/style.css">
<link rel="stylesheet"
        href="http://cdn.sencha.com/ext/beta/4.2.0.489/resources/css/ext-all.css" type="text/css"></link>
<link rel="stylesheet"
        href="http://cdn.sencha.com/ext/beta/4.2.0.489/examples/ux/css/ItemSelector.css" type="text/css"></link>
<link rel="stylesheet" type="text/css" href="http://cdn.sencha.com/ext/beta/4.2.0.489/examples/ux/grid/css/GridFilters.css" />
<link rel="stylesheet" type="text/css" href="http://cdn.sencha.com/ext/beta/4.2.0.489/examples/ux/grid/css/RangeMenu.css" />
<script type="text/javascript" src="http://cdn.sencha.com/ext/beta/4.2.0.489/ext-all.js"></script>
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
<li id="menu-item-1236" class="menu-item menu-item-type-post_type current-menu-item page_item page-item-293 current_page_item menu-item-1236"><a href="http://www.uva-bits.nl/virtual-lab/">Virtual Lab</a>
<ul>
<li class="app-item"><a href="${request.route_path('index')}">Script Wrapper</a>
-
<a href="."><%block name="title"/></a>
</li>
</ul>
</li>
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