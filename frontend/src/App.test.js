import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  test('renders pipeline heading', () => {
    render(<App />);
    expect(screen.getByText(/CI\/CD Showcase Pipeline/i)).toBeInTheDocument();
  });

  test('renders status badge', () => {
    render(<App />);
    expect(screen.getByTestId('status-badge')).toBeInTheDocument();
  });

  test('status transitions to healthy', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/HEALTHY/i)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  test('renders all 6 pipeline stages', () => {
    render(<App />);
    const stages = ['Build', 'Test', 'SonarCloud', 'Docker', 'Terraform', 'Deploy'];
    stages.forEach(stage => {
      expect(screen.getByText(stage)).toBeInTheDocument();
    });
  });

  test('renders version info', () => {
    render(<App />);
    expect(screen.getByTestId('version')).toBeInTheDocument();
  });

  test('renders environment info', () => {
    render(<App />);
    expect(screen.getByTestId('env')).toBeInTheDocument();
  });
});
