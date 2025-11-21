# Create Application

We're developing standalone apps in the `apps/` directory. These should be totallly portable and self-contained, and follow the examples in `examples/` for best practices.

We have developed and prototyped this agent in [OpenAI's Agent Builder](https://platform.openai.com/docs/guides/agent-builder)

And implmenting [OpenAI's ChatKit](https://platform.openai.com/docs/guides/chatkit).

Please familarize yourself with the above before we begin.

This repo is a FORK of the [OpenAI Chatkit Advanced Examples](https://github.com/openai/openai-chatkit-advanced-samples). As above, we will follow the examples in `examples/` for best practices. These are the tested offical examples and shoudl be viewed as a source of truth.

We will build a plan from the yaml specification in:

<path to spec yaml>
$ARGUMENTS
</path to spec yaml>

This yaml document is an overivew of the app we're building.

It contains a link to the workflow export code in workflow source. Please review and use that in our implmentation.

The frontend and backend yaml contain notes about the implemntation.

Please ask any clarifying questions before you write your plan.

You will write a plan to:

`specs/<appname>-plan.md

Once we have reviwed the plan and made finalizing chnages, please implment the app following best practices, and as cleanly and elegantly as possible.
