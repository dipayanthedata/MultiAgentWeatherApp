"""Multi-Agent Weather App — Gradio UI entry point."""

import gradio as gr

from agents.supervisor_agent import SupervisorAgent


supervisor = SupervisorAgent()

with gr.Blocks(title="Multi-Agent Weather Assistant") as demo:
    gr.Markdown("# 🌤️ Multi-Agent Weather Assistant")
    gr.Markdown(
        "Powered by five specialized AI agents — "
        "LocationResolver → WeatherData → SafetyEvaluator → "
        "ActivityAdvisor → ResponseComposer — "
        "coordinated by a SupervisorAgent on Databricks Apps."
    )

    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="Your Weather Question",
                placeholder="Should I hike Mission Peak this Saturday?",
                lines=2,
            )
            submit_btn = gr.Button("Ask the Agent Team", variant="primary")

    with gr.Row():
        output = gr.Markdown(label="Response")

    gr.Examples(
        examples=[
            ["Should I hike Mission Peak this Saturday?"],
            ["What's the weather in New York?"],
            ["Compare weather in London and Tokyo"],
            ["Is it safe to run outdoors in Miami today?"],
            ["Temperature in Berlin in celsius"],
        ],
        inputs=query_input,
    )

    submit_btn.click(fn=supervisor.run, inputs=query_input, outputs=output)
    query_input.submit(fn=supervisor.run, inputs=query_input, outputs=output)

demo.launch()
