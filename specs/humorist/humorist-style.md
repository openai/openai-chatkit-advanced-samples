I've been trying to develop an graphics style for Humorist that that uses the dots.

You can see that I've made some programmatic attempts in src/ Do not do these, but you can see that I'm trying to make art with dots.

Let's try this.

Look at the selected element in Figma. It's 384 by 384, and each of the circles are 8 pixels apart, and they have a diameter of 32 pixels. You can confirm this with the Figma design.What I'd like to make is a generator that will output this grid every time. But sometimes, those will be gone. The background will be no, and for each thing that is the subject of the icon or graphic, those will be on, and only one of the colors in the color palette.

Does this make sense?

First, write a procedural script that will generate these effects given the data.

Next, let's write a command for an AI agent and put that in Claude code. Tell it to take an image or an icon however the user prompts, and then from that prompt, visualize it in your head on this grid. Make sure that the background is always no, we're only showing this subject of the image because we want to make these like graphics.

Please output these files as SVG and PNG.

Ideally, there would just be an executable UV script that does this. The agent will generate the data and then feed it to the script.

This is a CLAUDE Code skill. In fact, let's make this a Claude Code skill.
