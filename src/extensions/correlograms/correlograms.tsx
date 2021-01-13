// LABBOX-EXTENSION: correlograms
// LABBOX-EXTENSION-TAGS: jupyter

import { ExtensionContext } from "../extensionInterface";
import AutoCorrelograms from "./AutoCorrelograms";
import CrossCorrelogramsView from "./CrossCorrelogramsView/CrossCorrelogramsView";

export function activate(context: ExtensionContext) {
    context.registerSortingView({
        name: 'Autocorrelograms',
        label: 'Autocorrelograms',
        priority: 50,
        component: AutoCorrelograms,
        singleton: true
    })
    context.registerSortingView({
        name: 'CrossCorrelograms',
        label: 'Cross-Correlograms',
        component: CrossCorrelogramsView,
        singleton: false
    })
}