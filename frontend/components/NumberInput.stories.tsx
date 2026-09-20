import type { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

import NumberInput from "./NumberInput"

const meta: Meta<typeof NumberInput> = {
  component: NumberInput,
  parameters: {
    layout: "padded",
  },
}

export default meta
type Story = StoryObj<typeof NumberInput>

// Wrap in state so the controls panel and interactions actually work
const Controlled = (args: React.ComponentProps<typeof NumberInput>) => {
  const [value, setValue] = useState(args.value)
  return <NumberInput {...args} value={value} onChange={setValue} />
}

export const WithSlider: Story = {
  render: (args) => <Controlled {...args} />,
  args: {
    label: "Legions",
    value: 3,
    min: 0,
    max: 10,
  },
}

export const NoSlider: Story = {
  render: (args) => <Controlled {...args} />,
  args: {
    label: "Talents",
    value: 0,
    min: 0,
  },
  parameters: {
    docs: {
      description: {
        story: "When only min (or only max) is provided, the slider is hidden.",
      },
    },
  },
}

export const Unbounded: Story = {
  render: (args) => <Controlled {...args} />,
  args: {
    label: "Count",
    value: 5,
  },
  parameters: {
    docs: {
      description: {
        story: "No min or max — both +/- buttons stay enabled at all times.",
      },
    },
  },
}

export const AtMinimum: Story = {
  render: (args) => <Controlled {...args} />,
  args: {
    label: "Legions",
    value: 0,
    min: 0,
    max: 10,
  },
}

export const AtMaximum: Story = {
  render: (args) => <Controlled {...args} />,
  args: {
    label: "Legions",
    value: 10,
    min: 0,
    max: 10,
  },
}

export const ZeroRange: Story = {
  render: (args) => <Controlled {...args} />,
  args: {
    label: "Bribe",
    value: 0,
    min: 0,
    max: 0,
  },
  parameters: {
    docs: {
      description: {
        story:
          "When min equals max, both buttons are disabled and the slider is hidden.",
      },
    },
  },
}
