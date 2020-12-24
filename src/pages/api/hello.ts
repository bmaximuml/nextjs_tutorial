import { NextApiRequest, NextApiResponse } from 'next'

export default (_: NextApiRequest, res: NextApiResponse) => {
// export default function handler(req, res) {
    res.status(200).json({ text: 'Hello' })
}