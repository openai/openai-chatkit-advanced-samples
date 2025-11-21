# Create Application

We're developing standalone apps using OpenAI's AgentKit, Agent Builder, and ChatKit, in the `apps/` directory. These apps should be totallly portable and self-contained, and follow the examples in `examples/` for best practices.

We have developed and prototyped this the app's workflow and agents in [OpenAI's Agent Builder](https://platform.openai.com/docs/guides/agent-builder)

We are now making an app, integrating these agents with [OpenAI's ChatKit](https://platform.openai.com/docs/guides/chatkit)/

Please familarize yourself with the above before we begin.

This repo is a FORK of the [OpenAI Chatkit Advanced Examples](https://github.com/openai/openai-chatkit-advanced-samples).

**IMPORTANT:** We will follow the examples in `examples/` for best practices. These are the tested offical examples and should be viewed as a source of truth.

We will build a plan from the yaml specification in:

<path to spec yaml>
$ARGUMENTS
</path to spec yaml>

This yaml document is an overview of the app we're building. Please review all the documents and files listed in the yaml file.

It must contain a path to the workflow export code in workflow source. Please review and use that in our implmentation.

The frontend and backend yaml contain notes about the implemntation, and may link to more specification docs. Please read those and do any research into best practices relevant to its implementation.

Please ask any clarifying questions before you write your plan.

You will write a plan to:

`specs/<appname>-plan.md

Once we have reviwed the plan and made finalizing chnages, please implment the app following best practices, as cleanly and elegantly as possible.
