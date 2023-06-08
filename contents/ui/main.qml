/*
    SPDX-FileCopyrightText: 2022 author-name
    SPDX-License-Identifier: GPL-3.0-or-later
*/

import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12

import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.extras 2.0 as PlasmaExtras

Item {
    id: root

    Plasmoid.preferredRepresentation: Plasmoid.compactRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.ConfigurableBackground
    property bool horizontal: plasmoid.formFactor !== PlasmaCore.Types.Vertical

    property string labelText: plasmoid.configuration.identifier == "-1" ? "root" : plasmoid.configuration.identifier
    property string labelBG: plasmoid.configuration.identifier == "-1" ? "black" : "white"



    Plasmoid.compactRepresentation: Item {
        id: root

        Layout.fillWidth: horizontal ? false : true
        Layout.fillHeight: horizontal ? true : false

        PlasmaComponents.Label {
            id: label
            anchors.fill: parent
            text: labelText
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            background: Rectangle {
                color: labelBG
                opacity: 0.3
            }
            opacity: Plasmoid.editMode ? 1.0 : 0.0
        }

        Rectangle {
            id: edgeLine
            color: "transparent"
            border.color: "#66f1f1f2"
            x: horizontal ? root.width : -10 * units.devicePixelRatio
            y: horizontal ? -10 * units.devicePixelRatio : root.height
            width: horizontal ? (1 * units.devicePixelRatio) : (root.width + 20 * units.devicePixelRatio)
            height: horizontal ? (root.height + 20 * units.devicePixelRatio) : (1 * units.devicePixelRatio)
            border.width: 1 * units.devicePixelRatio
            opacity: Plasmoid.configuration.hiddenMode ? 0.0 : Plasmoid.editMode ? 0.0 : 1.0
        }
    }

    PlasmaCore.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []
        onNewData: disconnectSource(sourceName)

        function exec(cmd) {
            executable.connectSource(cmd)
        }
    }

    function action_syncPanels() {
        executable.exec("'../code/panel_updater'");
    }

    function initActions() {
        Plasmoid.setAction("syncPanels", i18nc("@action", "Sync Displays…"), "view-refresh");
        Plasmoid.setActionSeparator("EndofGroup2");
    }

    Component.onCompleted: {
        initActions();
    }
}
