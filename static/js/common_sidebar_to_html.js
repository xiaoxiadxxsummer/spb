function sidebar_to_html(){
    document.getElementById('system_sidebar').innerHTML = '<div>' +
        ' <h1 class="visually-hidden">Sidebars examples</h1>\n' +
        '\n' +
        '  <div class="d-flex flex-column flex-shrink-0 p-3 text-bg-dark" style="width: 280px;">\n' +
        '    <a href="/" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">\n' +
        '      <svg class="bi pe-none me-2" width="40" height="32"><use xlink:href="#bootstrap"/></svg>\n' +
        '      <span class="fs-4">Sidebar</span>\n' +
        '    </a>\n' +
        '    <hr>\n' +
        '    <ul class="nav nav-pills flex-column mb-auto">\n' +
        '      <li class="nav-item">\n' +
        '        <a href="#" class="nav-link" aria-current="page">\n' +
        '          <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#home"/></svg>\n' +
        '          Home\n' +
        '        </a>\n' +
        '      </li>\n' +
        '      <li>\n' +
        '        <a href="#" class="nav-link text-white">\n' +
        '          <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#speedometer2"/></svg>\n' +
        '          Dashboard\n' +
        '        </a>\n' +
        '      </li>\n' +
        '      <li>\n' +
        '        <a href="#" class="nav-link text-white">\n' +
        '          <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#table"/></svg>\n' +
        '          Orders\n' +
        '        </a>\n' +
        '      </li>\n' +
        '      <li>\n' +
        '        <a href="#" class="nav-link text-white">\n' +
        '          <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#grid"/></svg>\n' +
        '          Products\n' +
        '        </a>\n' +
        '      </li>\n' +
        '      <li>\n' +
        '        <a href="#" class="nav-link text-white active">\n' +
        '          <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#people-circle"/></svg>\n' +
        '          Customers\n' +
        '        </a>\n' +
        '      </li>\n' +
        '    </ul>\n' +
        '    <hr>\n' +
        '    <div class="dropdown">\n' +
        '      <a href="#" class="d-flex align-items-center text-white text-decoration-none dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">\n' +
        '        <img src="https://github.com/mdo.png" alt="" width="32" height="32" class="rounded-circle me-2">\n' +
        '        <strong>mdo</strong>\n' +
        '      </a>\n' +
        '      <ul class="dropdown-menu dropdown-menu-dark text-small shadow">\n' +
        '        <li><a class="dropdown-item" href="#">New project...</a></li>\n' +
        '        <li><a class="dropdown-item" href="#">Settings</a></li>\n' +
        '        <li><a class="dropdown-item" href="#">Profile</a></li>\n' +
        '        <li><hr class="dropdown-divider"></li>\n' +
        '        <li><a class="dropdown-item" href="#">Sign out</a></li>\n' +
        '      </ul>\n' +
        '    </div>\n' +
        '  </div>\n' +
        '  <div class="b-example-divider b-example-vr"></div>' +
        '</div>'
}