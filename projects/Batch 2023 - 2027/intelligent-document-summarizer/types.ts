/**
 * Defines the structure for a single message in the chat interface.
 */
export interface ChatMessage {
  /** The role of the message sender, either the user or the AI model. */
  role: 'user' | 'model';
  /** The text content of the message. */
  text: string;
  /** The timestamp when the message was created. */
  timestamp: Date;
  /** An optional flag to indicate if the message is an error message. */
  error?: boolean;
}