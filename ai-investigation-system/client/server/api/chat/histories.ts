import { sub } from 'date-fns'
import type { ChatHistory } from '~/types'

const chatHistories: ChatHistory[] = [{
  id: '1',
  caseId: 'case-001',
  caseName: 'Fraudulent Transaction Analysis - Account #XY789',
  title: 'High-Value Transfer Investigation',
  messages: [
    {
      id: '1',
      role: 'user',
      content: 'Can you analyze the suspicious transfer of $50,000 that occurred on March 15th?',
      timestamp: sub(new Date(), { hours: 8 }).toISOString()
    },
    {
      id: '2',
      role: 'assistant',
      content: 'I\'ve analyzed the transaction. The transfer was made to account 987654321 at 2:45 AM, which is unusual for this account\'s typical behavior. The receiving account shows signs of being a shell company. Flagging for immediate review.',
      timestamp: sub(new Date(), { hours: 8, minutes: 2 }).toISOString()
    },
    {
      id: '3',
      role: 'user',
      content: 'What about the IP address origin?',
      timestamp: sub(new Date(), { hours: 7, minutes: 55 }).toISOString()
    },
    {
      id: '4',
      role: 'assistant',
      content: 'The IP address is registered in a different country than the customer\'s usual location. Combined with the timing and amount, this meets our high-risk criteria. Recommend freezing related accounts.',
      timestamp: sub(new Date(), { hours: 7, minutes: 50 }).toISOString()
    }
  ],
  createdAt: sub(new Date(), { days: 3 }).toISOString(),
  updatedAt: sub(new Date(), { hours: 8 }).toISOString()
}, {
  id: '2',
  caseId: 'case-002',
  caseName: 'Credit Card Clone Detection - Card #****4532',
  title: 'Multiple Unauthorized Charges',
  messages: [
    {
      id: '1',
      role: 'user',
      content: 'We\'ve detected 15 unauthorized charges totaling $3,200 across different merchants. Where should we start?',
      timestamp: sub(new Date(), { days: 1, hours: 10 }).toISOString()
    },
    {
      id: '2',
      role: 'assistant',
      content: 'These charges follow a pattern typical of cloned cards. I\'m analyzing merchant locations and times. The pattern suggests multiple locations within a 50-mile radius over 6 hours.',
      timestamp: sub(new Date(), { days: 1, hours: 10, minutes: 5 }).toISOString()
    },
    {
      id: '3',
      role: 'user',
      content: 'Can you cross-reference with security camera footage?',
      timestamp: sub(new Date(), { days: 1, hours: 9, minutes: 50 }).toISOString()
    },
    {
      id: '4',
      role: 'assistant',
      content: 'I\'ve compiled a list of merchants to contact for footage. Three locations have agreed to provide CCTV. Initial review shows two suspects appearing at multiple locations during transaction times.',
      timestamp: sub(new Date(), { days: 1, hours: 9, minutes: 40 }).toISOString()
    },
    {
      id: '5',
      role: 'user',
      content: 'Good work. Issue a new card and initiate a chargeback.',
      timestamp: sub(new Date(), { days: 1, hours: 9, minutes: 30 }).toISOString()
    }
  ],
  createdAt: sub(new Date(), { days: 5 }).toISOString(),
  updatedAt: sub(new Date(), { days: 1, hours: 10 }).toISOString()
}, {
  id: '3',
  caseId: 'case-003',
  caseName: 'Account Takeover Investigation - User ID: usr_45829',
  title: 'Unauthorized Login & Password Change',
  messages: [
    {
      id: '1',
      role: 'user',
      content: 'Customer reports their account was compromised. Password was changed and funds transferred. What\'s the timeline?',
      timestamp: sub(new Date(), { hours: 2 }).toISOString()
    },
    {
      id: '2',
      role: 'assistant',
      content: 'Timeline Analysis:\n- 11:23 PM: Suspicious login from Mumbai IP\n- 11:28 PM: Password changed\n- 11:32 PM: Transfer of $8,500 initiated\n- 11:35 PM: Logout\n\nThe account had 2FA enabled but it was disabled at 11:22 PM.',
      timestamp: sub(new Date(), { hours: 1, minutes: 55 }).toISOString()
    },
    {
      id: '3',
      role: 'user',
      content: 'Can we reverse the transfer?',
      timestamp: sub(new Date(), { hours: 1, minutes: 50 }).toISOString()
    },
    {
      id: '4',
      role: 'assistant',
      content: 'The receiving account is already empty. However, I\'ve issued a hold on the transfer destination account at the partner bank. There\'s a 48-hour window to recover the funds. Recommend contacting law enforcement for the international component.',
      timestamp: sub(new Date(), { hours: 1, minutes: 45 }).toISOString()
    }
  ],
  createdAt: sub(new Date(), { days: 7 }).toISOString(),
  updatedAt: sub(new Date(), { hours: 2 }).toISOString()
}, {
  id: '4',
  caseId: 'case-004',
  caseName: 'Phishing Scheme Investigation - Multiple Accounts',
  title: 'Coordinated Phishing Attack Analysis',
  messages: [
    {
      id: '1',
      role: 'user',
      content: 'We\'ve received 47 reports of phishing emails impersonating our bank. All occurred within 2 hours. What\'s your assessment?',
      timestamp: sub(new Date(), { days: 2, hours: 14 }).toISOString()
    },
    {
      id: '2',
      role: 'assistant',
      content: 'This is a coordinated attack. Email header analysis shows originating from botnets spanning 12 countries. The phishing URL mimics our login page almost perfectly. 8% of recipients (likely 4-5 accounts) may have provided credentials.',
      timestamp: sub(new Date(), { days: 2, hours: 14, minutes: 5 }).toISOString()
    },
    {
      id: '3',
      role: 'user',
      content: 'Have any compromised accounts shown suspicious activity?',
      timestamp: sub(new Date(), { days: 2, hours: 13, minutes: 50 }).toISOString()
    },
    {
      id: '4',
      role: 'assistant',
      content: 'Yes - 3 accounts have attempted transfers within 30 minutes of phishing receipt. Our fraud detection blocked them automatically. I\'ve identified the attacker network and forwarded details to cybersecurity. Recommend sending security alerts to all affected customers.',
      timestamp: sub(new Date(), { days: 2, hours: 13, minutes: 40 }).toISOString()
    },
    {
      id: '5',
      role: 'user',
      content: 'Update all affected customers and initiate fraud monitoring on their accounts.',
      timestamp: sub(new Date(), { days: 2, hours: 13, minutes: 30 }).toISOString()
    }
  ],
  createdAt: sub(new Date(), { days: 10 }).toISOString(),
  updatedAt: sub(new Date(), { days: 2, hours: 14 }).toISOString()
}, {
  id: '5',
  caseId: 'case-005',
  caseName: 'Money Laundering Pattern Detection - Business Account',
  title: 'Suspicious Structured Deposits Investigation',
  messages: [
    {
      id: '1',
      role: 'user',
      content: 'Business account has been making multiple deposits of exactly $9,900 each day for the past 2 weeks. This looks like structuring to avoid reporting thresholds.',
      timestamp: sub(new Date(), { days: 4, hours: 11 }).toISOString()
    },
    {
      id: '2',
      role: 'assistant',
      content: 'Classic structuring pattern detected. 14 deposits of $9,900 = $138,600 total, staying just below $10,000 AML threshold. Deposits from 7 different sources, all to same business account. Then rapid disbursements to wire services.',
      timestamp: sub(new Date(), { days: 4, hours: 11, minutes: 5 }).toISOString()
    },
    {
      id: '3',
      role: 'user',
      content: 'What\'s the business ostensibly doing?',
      timestamp: sub(new Date(), { days: 4, hours: 10, minutes: 55 }).toISOString()
    },
    {
      id: '4',
      role: 'assistant',
      content: 'Registered as "Import/Export Consulting" but business license is inactive. No registered employees. Wire destinations include shell companies in offshore jurisdictions. High-confidence money laundering indicator. Filing SAR (Suspicious Activity Report) recommended.',
      timestamp: sub(new Date(), { days: 4, hours: 10, minutes: 50 }).toISOString()
    },
    {
      id: '5',
      role: 'user',
      content: 'Block the account and file the SAR immediately.',
      timestamp: sub(new Date(), { days: 4, hours: 10, minutes: 40 }).toISOString()
    },
    {
      id: '6',
      role: 'assistant',
      content: 'Account blocked and SAR filed with FinCEN. All pending transactions frozen. Regulatory notification sent.',
      timestamp: sub(new Date(), { days: 4, hours: 10, minutes: 35 }).toISOString()
    }
  ],
  createdAt: sub(new Date(), { days: 12 }).toISOString(),
  updatedAt: sub(new Date(), { days: 4, hours: 11 }).toISOString()
}]

export default eventHandler(async () => {
  return chatHistories
})
