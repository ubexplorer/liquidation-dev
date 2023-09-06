odoo.define("dgf_board_patch.BoardView", function (require) {
  "use strict";

  const BoardView = require("board.BoardView");
  const core = require("web.core");
  const dataManager = require("web.data_manager");

  var QWeb = core.qweb;

  debugger
  // BoardView.prototype.config.Controller
  BoardView.prototype.config.Controller.include({
    custom_events: _.extend(
      {},
      BoardView.prototype.config.Controller.prototype.custom_events,
      {
        save_dashboard: "_saveDashboard",
      }
    ),

    /**Actually save a dashboard
     * @OverRide
     * @returns {Promise}
     */
    _saveDashboard: function () {
      debugger
      var board = this.renderer.getBoard();
      var arch = QWeb.render("DashBoard.xml", _.extend({}, board));
      return this._rpc({
        route: "/web/view/edit_custom",
        params: {
          custom_id: this.customViewID ? this.customViewID : "",
          arch: arch,
        },
      }).then(dataManager.invalidate.bind(dataManager));
    },
  });
});
