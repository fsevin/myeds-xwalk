# Your Project's Title...
Your project's description...

## Environments
- Preview: https://main--{repo}--{owner}.aem.page/
- Live: https://main--{repo}--{owner}.aem.live/

## Documentation

Before using the aem-boilerplate, we recommand you to go through the documentation on [www.aem.live](https://www.aem.live/docs/) and [experienceleague.adobe.com](https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/edge-delivery/wysiwyg-authoring/authoring), more specifically:
1. [Getting Started](https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/edge-delivery/wysiwyg-authoring/edge-dev-getting-started), [Creating Blocks](https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/edge-delivery/wysiwyg-authoring/create-block), [Content Modelling](https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/edge-delivery/wysiwyg-authoring/content-modeling)
2. [The Anatomy of a Project](https://www.aem.live/developer/anatomy-of-a-project)
3. [Web Performance](https://www.aem.live/developer/keeping-it-100)
4. [Markup, Sections, Blocks, and Auto Blocking](https://www.aem.live/developer/markup-sections-blocks)

Furthremore, we encourage you to watch the recordings of any of our previous presentations or sessions:
- [Getting started with AEM Authoring and Edge Delivery Services](https://experienceleague.adobe.com/en/docs/events/experience-manager-gems-recordings/gems2024/aem-authoring-and-edge-delivery)

## Prerequisites

- nodejs 18.3.x or newer
- AEM Cloud Service release 2024.8 or newer (>= `17465`)

## Installation

```sh
npm i
```

## Linting

```sh
npm run lint
```

## Local development

1. Create a new repository based on the `aem-boilerplate` template
1. Add the [AEM Code Sync GitHub App](https://github.com/apps/aem-code-sync) to the repository
1. Install the [AEM CLI](https://github.com/adobe/helix-cli): `npm install -g @adobe/aem-cli`
1. Start AEM Proxy: `aem up` (opens your browser at `http://localhost:3000`)
1. Open the `{repo}` directory in your favorite IDE and start coding :)

## AI Image display

The AI Image block's aspect ratio setting controls the generated image dimensions.
Both the generation preview in Universal Editor and the saved image display the
complete image without cropping, preserving its aspect ratio as the screen changes.
Images are centered, constrained to the block width, and capped at the smaller of
60% of the viewport height or 600px. Portrait and square images may therefore leave
space on either side rather than filling the block width. No Smart Crop service is
required for this display behavior.
