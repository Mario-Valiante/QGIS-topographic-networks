# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TopographicNetworks
                                 A QGIS plugin
 Creation and analysis of topographic (surface) networks.
                             -------------------
        begin                : 2014-10-26
        copyright            : (C) 2014 by Zoran Čučković
        email                : /
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load TopographicNetworks class from file TopographicNetworks.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .topographic_networks import TopographicNetworks
    return TopographicNetworks(iface)
