import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatusBadge, { STATUS_COLORS } from '../components/StatusBadge'
import { EmptyState, ErrorBox, SuccessBox } from '../components/Feedback'

describe('StatusBadge', () => {
  it('renders every workflow status with a mapped style', () => {
    for (const status of Object.keys(STATUS_COLORS)) {
      const { unmount } = render(<StatusBadge status={status} />)
      expect(screen.getByText(status)).toBeInTheDocument()
      unmount()
    }
  })
  it('falls back gracefully for unknown statuses', () => {
    render(<StatusBadge status="Something Else" />)
    expect(screen.getByText('Something Else')).toBeInTheDocument()
  })
})

describe('Feedback components', () => {
  it('EmptyState shows title and hint', () => {
    render(<EmptyState title="No issues" hint="Adjust filters" />)
    expect(screen.getByText('No issues')).toBeInTheDocument()
    expect(screen.getByText('Adjust filters')).toBeInTheDocument()
  })
  it('ErrorBox renders alert role, SuccessBox renders status role', () => {
    render(<><ErrorBox message="boom" /><SuccessBox message="saved" /></>)
    expect(screen.getByRole('alert')).toHaveTextContent('boom')
    expect(screen.getByRole('status')).toHaveTextContent('saved')
  })
  it('ErrorBox renders nothing without a message', () => {
    const { container } = render(<ErrorBox message="" />)
    expect(container).toBeEmptyDOMElement()
  })
})
