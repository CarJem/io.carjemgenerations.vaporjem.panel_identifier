/*
    SPDX-FileCopyrightText: 2022 author-name
    SPDX-License-Identifier: GPL-3.0-or-later
*/

import QtQuick 2.12
import QtQuick.Controls 2.12 as QtControls
import QtQuick.Layouts 1.15 as QtLayouts

import org.kde.kirigami 2.3 as Kirigami

Kirigami.FormLayout {
    id: generalPage
    width: childrenRect.width
    height: childrenRect.height

    property alias cfg_allDisplays: allDisplays.checked

    QtControls.CheckBox {
        id: allDisplays
        Kirigami.FormData.label: i18n("Show on all Displays:")
        visible: plasmoid.configuration.identifier == "-1" ? true : false
    }

    Item {
        Kirigami.FormData.isSection: true
    }
}
