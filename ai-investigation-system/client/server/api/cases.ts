import { caseService } from '~/services/caseService'

export default eventHandler(async () => {
  return await caseService.getCases()
})
