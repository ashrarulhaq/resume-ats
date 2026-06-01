import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

test('renders the resume tailor app shell', async () => {
  const container = document.createElement('div');
  document.body.appendChild(container);

  const root = createRoot(container);
  await React.act(async () => {
    root.render(<App />);
  });

  expect(container.textContent).toMatch(/resume tailor/i);
  expect(container.textContent).toMatch(/please enter your openrouter api key/i);

  await React.act(async () => {
    root.unmount();
  });
  document.body.removeChild(container);
});
