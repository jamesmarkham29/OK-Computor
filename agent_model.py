from pydantic import BaseModel
from agents import Agent, ModelSettings, TResponseInputItem, Runner, RunConfig, trace
from openai.types.shared.reasoning import Reasoning

class PhilosipherFinderSchema(BaseModel):
  found: bool
  philosopher_name: str


class PersonFinderSchema(BaseModel):
  person_found: bool
  person_name: str


philosopher_quote_finder = Agent(
  name="Philosopher quote finder",
  instructions="Using the name of the philosopher give 5 other of their quotes that are similar ",
  model="gpt-5.5",
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


philosipher_finder = Agent(
  name="Philosipher finder",
  instructions="You are going to receive quotes and you will find the philosopher of that quote state it",
  model="gpt-5.5",
  output_type=PhilosipherFinderSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


person_finder = Agent(
  name="Person finder",
  instructions="Look for someone who has said this quote not only philosophers. ",
  model="gpt-5.5",
  output_type=PersonFinderSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


quote_finder = Agent(
  name="Quote finder",
  instructions="with the persons name state what they do and of they have other quotes, if they do say max of 5 their quotes.",
  model="gpt-5.5",
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("Philosipher quote"):
    state = {

    }
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    philosipher_finder_result_temp = await Runner.run(
      philosipher_finder,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_6a15e7febf34819080f0dd9932afea6a053e8c543e16c4f3"
      })
    )

    conversation_history.extend([item.to_input_item() for item in philosipher_finder_result_temp.new_items])

    philosipher_finder_result = {
      "output_text": philosipher_finder_result_temp.final_output.json(),
      "output_parsed": philosipher_finder_result_temp.final_output.model_dump()
    }
    if philosipher_finder_result["output_parsed"]["found"]:
      philosopher_quote_finder_result_temp = await Runner.run(
        philosopher_quote_finder,
        input=[
          *conversation_history
        ],
        run_config=RunConfig(trace_metadata={
          "__trace_source__": "agent-builder",
          "workflow_id": "wf_6a15e7febf34819080f0dd9932afea6a053e8c543e16c4f3"
        })
      )

      conversation_history.extend([item.to_input_item() for item in philosopher_quote_finder_result_temp.new_items])

      philosopher_quote_finder_result = {
        "output_text": philosopher_quote_finder_result_temp.final_output_as(str)
      }
      return philosopher_quote_finder_result
    else:
      person_finder_result_temp = await Runner.run(
        person_finder,
        input=[
          *conversation_history
        ],
        run_config=RunConfig(trace_metadata={
          "__trace_source__": "agent-builder",
          "workflow_id": "wf_6a15e7febf34819080f0dd9932afea6a053e8c543e16c4f3"
        })
      )

      conversation_history.extend([item.to_input_item() for item in person_finder_result_temp.new_items])

      person_finder_result = {
        "output_text": person_finder_result_temp.final_output.json(),
        "output_parsed": person_finder_result_temp.final_output.model_dump()
      }
      if person_finder_result["output_parsed"]["person_found"]:
        quote_finder_result_temp = await Runner.run(
          quote_finder,
          input=[
            *conversation_history
          ],
          run_config=RunConfig(trace_metadata={
            "__trace_source__": "agent-builder",
            "workflow_id": "wf_6a15e7febf34819080f0dd9932afea6a053e8c543e16c4f3"
          })
        )

        conversation_history.extend([item.to_input_item() for item in quote_finder_result_temp.new_items])

        quote_finder_result = {
          "output_text": quote_finder_result_temp.final_output_as(str)
        }
        return quote_finder_result
      else:
        return person_finder_result
